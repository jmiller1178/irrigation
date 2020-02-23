# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime, date, timedelta
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.http import  JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from . models import (RpiGpioRequest, RpiGpio, Zone, Status,
                      WeatherCondition, IrrigationSystem, Schedule)
from sprinklesmart.gpio.controller import (turn_zone_on, turn_zone_off, turn_24_vac_off,
                                           turn_24_vac_on, turn_all_zone_outputs_off,
                                           irrigation_system_enabled, turn_irrigation_system_active_off,
                                           turn_irrigation_system_active_on)
from . serializers import (IrrigationSystemSerializer, WeatherConditionSerializer, 
                           ZoneSerializer, RpiGpioRequestSerializer, ScheduleSerializer)
from rest_framework.renderers import JSONRenderer

import logging

logger = logging.getLogger(__name__)

# main browser based view for the irrigation website
# /index.html
def index(request):
    zones = Zone.objects.filter(enabled=True)
    serializer = ZoneSerializer(zones, many=True)
    zone_list_json = json.dumps(serializer.data)
       
    # latest WeatherCondtion
    current_weather_condition = WeatherCondition.objects.filter().order_by('-id')[0]
    serializer = WeatherConditionSerializer(current_weather_condition, many=False)
    current_weather_conditions_json = json.dumps(serializer.data)

    todays_requests = RpiGpioRequest.todays_requests.all()
    serializer = RpiGpioRequestSerializer(todays_requests, many=True)
    todays_requests_json = json.dumps(serializer.data)

    irrigation_system = IrrigationSystem.objects.get(pk=1)
    serializer = IrrigationSystemSerializer(irrigation_system, many=False)
    irrigation_system_json = json.dumps(serializer.data)

    serializer = ZoneSerializer(irrigation_system.system_enabled_zone, many=False)
    system_enabled_zone_json = json.dumps(serializer.data)
    
    # next look for the RpiGpio associated to system enabling - this one will enable the 24VAC to the valve control relays
    serializer = ZoneSerializer(irrigation_system.valves_enabled_zone, many=False)
    valves_enabled_zone_json = json.dumps(serializer.data)


    serializer = IrrigationSystemSerializer(irrigation_system, many=False)
    irrigation_system = json.dumps(serializer.data)

    return render(request, 'index.html',
                        {
                            'irrigation_system': irrigation_system_json,
                            'system_enabled_zone_data' : system_enabled_zone_json,
                            'valves_enabled_zone_data' : valves_enabled_zone_json,
                            'zone_list' : zone_list_json,
                            'todays_requests' : todays_requests_json,
                            'current_weather_conditions' : current_weather_conditions_json,
                        })


# web browser view invoked when the page for manually scheduling zone activities is loaded
# /manually_schedule.html
@ensure_csrf_cookie
def manually_schedule(request):
    schedules = Schedule.objects.all()
    serializer = ScheduleSerializer(schedules, many=True)    
    schedules_json = json.dumps(serializer.data)

    return render(request, 'manually_schedule.html',
                        {
                            'schedules': schedules_json,
                        })

# this is the command that is invoked when the user is on the manual schedule page and they click
# the "Schedule" button at the bottom of the page
def create_schedule(request):
    if request.method == 'POST':
      # 1st turn off all outputs
      turn_all_zone_outputs_off()
        
      # 2nd cancel any upcoming scheduled requests for today
      cancel_all_current_requests()
      
      # need a list of the zones
      zone_list = Zone.objects.filter(visible=True, enabled=True)
      # retrieve the start time from the form field "start_time" and tack on today's date
      startTime = datetime.strptime(str(date.today()) + ' ' + request.POST['start_time'], "%Y-%m-%d %H:%M")
      # we need a status object of "New" instantiated
      new_status = get_object_or_404(Status, pk=1)
      # now we have to iterate through the table data and put the requests in the database
      for zone in zone_list:
          # see if the user has checked the box for the current zone chkZone_1, chkZone_2, etc.
        if(request.POST.__contains__('chkZone_' + str(zone.zoneId))):
          endTime = startTime + timedelta(minutes=int(request.POST['duration_'+ str(zone.zoneId)]))
          rpiGpio = RpiGpio.objects.get(zone=zone)
          
          # instantiate and fill up an RpiGpioRequest to turn on the zone and save it
          rpiGpioRequest = RpiGpioRequest.objects.create(rpiGpio=rpiGpio, status=new_status, onDateTime=startTime, offDateTime=endTime)
          rpiGpioRequest.save()
          startTime = endTime

    return HttpResponseRedirect('/')



def turn_all_outputs_off():
    """
    if there are any zone outputs currently ON, we should find an active RPiGPIORequest record
    with a status of 4 which means "In Progress"
    """
    active_requests = RpiGpioRequest.pending_or_active_requests.all()
    current_time_plus_1_minutes = (datetime.now() + timedelta(seconds=15)).strftime("%H:%M")
    new_off_date_time =  datetime.strptime(str(date.today()) + ' ' + current_time_plus_1_minutes, "%Y-%m-%d %H:%M")
    for rpiGpioRequest in active_requests:
        # override the offDateTime value for the "In Progress" request so that it is turned OFF 
        # by the Daemon
        rpiGpioRequest.offDateTime = new_off_date_time
        rpiGpioRequest.save()       


def cancel_all_current_requests():
    """
    cancel any upcoming scheduled requests for today
    instantiate a Status of "Cancelled"
    """
    cancelled_status = get_object_or_404(Status, pk=3)
    # retrieve all new requests
    todays_requests = RpiGpioRequest.objects.filter(status__in=[1], onDateTime__contains=date.today())

    # mark them as cancelled
    for rpiGpioRequest in todays_requests:
        rpiGpioRequest.status = cancelled_status
        rpiGpioRequest.save()


def rpi_gpio_request_cancel(request, id):
    rpiGpioOnRequest = get_object_or_404(RpiGpioRequest, pk=id)
    cancelled_status = get_object_or_404(Status, pk=3)
    # cancel the ON request
    rpiGpioOnRequest.status = cancelled_status
    rpiGpioOnRequest.save()
    return HttpResponseRedirect('/')

    
def rpi_gpio_request_cancel_all(request):
    # 1 is pending 4 is active
    rpiGpioOnRequests = RpiGpioRequest.pending_or_active_requests.all()
    cancelled_status = get_object_or_404(Status, pk=3)
    # cancel the ON requests
    for rpiGpioOnRequest in rpiGpioOnRequests:
        rpiGpioOnRequest.status = cancelled_status
        rpiGpioOnRequest.save()
    return HttpResponseRedirect('/')


@require_http_methods(["GET"])
def get_schedule(request, scheduleId):
    scheduleId = int(scheduleId)
    schedule = get_object_or_404(Schedule,  pk=scheduleId)
    queryset = schedule.irrigationschedule_set.all()
    serializer = IrrigationScheduleSerializer(queryset, many=True)

    return JsonResponse(serializer.data, safe=False)

@require_POST
def toggle_zone(request):
    response = {}
    irrigation_system = IrrigationSystem.objects.get(pk=1)
    json_data = json.loads(request.body.decode('utf-8'))
    zone_id = json_data['zoneId']
    success = True
    error = "No Errors"

    # read the Zone info from the database
    try:
        zone = Zone.objects.get(pk=zone_id)

        # check to see if it is in an ON state
        if zone.is_on:
            zone = turn_zone_off(zone_id)
        else: 
            # only allow zones to turn on if the irrigation_system is enabled
            # unless the zone we're trying to turn on is the one for enabling the
            # irrigation system - in that case we're trying to re-enable the system
            rpiGpio = RpiGpio.objects.get(zone=zone)  
            if zone == irrigation_system.system_enabled_zone:
                zone = turn_zone_on(zone_id)
            elif irrigation_system_enabled():
                zone = turn_zone_on(zone_id)
            else:
                error = "Irrigation System NOT Enabled"
                success = False
    
        serializer = ZoneSerializer(zone, many=False)
        response['zone'] = json.dumps(serializer.data)
        response['error'] = error
        response['success'] = success

    except Zone.DoesNotExist:
        response['zone'] = None
        response['error'] = "Zone {0} PK NOT FOUND".format(zone_id)
        response['success'] = False

    return JsonResponse(response)

@require_POST
def toggle_system_mode(request):
    irrigation_system = IrrigationSystem.objects.get(pk=1)
    irrigation_system = irrigation_system.toggle_system_mode()

    # whenever we toggle from Manual to Automatic (or vice versa)
    # we need to turn all zones off
    turn_all_zone_outputs_off()

    serializer = IrrigationSystemSerializer(irrigation_system, many=False)

    return JsonResponse(serializer.data, safe=False)

@require_POST
def toggle_zone_request(request):
    json_data = json.loads(request.body.decode('utf-8'))
    zone_id = json_data['zoneId']
    logger.info(zone_id)
    cancelled_status = Status.objects.get(pk=3) # 3 is Cancel
    
    rpi_gpio_on_requests = RpiGpioRequest.pending_or_active_requests.filter(rpiGpio__zone__zoneId=zone_id)
    for rpi_gpio_on_request in rpi_gpio_on_requests:
        # cancel the ON request
        rpi_gpio_on_request.status = cancelled_status
        rpi_gpio_on_request.save()
    
    serializer = RpiGpioRequestSerializer(rpi_gpio_on_requests, many=True)

    return JsonResponse(serializer.data, safe=False)