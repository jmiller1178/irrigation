# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from . models import RpiGpioRequest, RpiGpio, Zone, Status,\
      WeatherCondition, IrrigationSystem, Schedule
from datetime import datetime, date, timedelta
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from sprinklesmart.gpio.controller import *
from . serializers import IrrigationScheduleSerializer
from django.views.decorators.http import require_http_methods
from django.http import  JsonResponse
from django.views.decorators.http import require_GET, require_POST
import json

# main browser based view for the irrigation website
# /index.html
def index(request):
    zone_list = Zone.objects.filter(visible=True, enabled=True)
    current_date = datetime.now()
    todays_requests = RpiGpioRequest.objects.filter(status__in=[1,4],\
    onDateTime__contains=date.today())

    # latest WeatherCondtion
    current_weather = WeatherCondition.objects.order_by('-id')[0]
    
    # 1st look for the IrrigationSystem.systemState
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    system_enabled = system_enabled_rpi_gpio.zone.is_on
    
    # next look for the RpiGpio associated to system enabling - this one will enable the 24VAC to the valve control relays
    twentyfour_vac_active_rpi_gpio = RpiGpio.objects.get(gpioName=settings.IRRIGATION_ACTIVE_GPIO)
    twentyfour_vac_active = twentyfour_vac_active_rpi_gpio.zone.is_on
    
    return render(request, 
                'index.html', 
                {
                  'zone_list' : zone_list,
                  'current_date' : current_date,
                  'todays_requests' : todays_requests,
                  'current_weather' : current_weather,
                  'system_enabled' : system_enabled,
                  'twentyfour_vac_enabled' : twentyfour_vac_active,
                })
                              
                              
def dashboard(request):
    active_status = get_object_or_404(Status, pk=4) 
    
    # this is the GPIO which enables 24VAC to the valve control relays 	
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    twentyfour_vac_enabled = system_enabled_rpi_gpio.zone.is_on

    # get the current weatherconditions
    current_weather = WeatherCondition.objects.order_by('-id')[0]
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    system_enabled = irrigation_system.systemState
    active_request = RpiGpioRequest.objects.get(status=active_status)
    return render(request, 
                'dashboard.html', 
                    {
                    'current_weather' : current_weather,
                    'system_enabled' : system_enabled,
                    'active_request' : active_request,
                    'twentyfour_vac_enabled' : twentyfour_vac_enabled,
                    })

# web browser single zone control view
# /zone_control.html
@ensure_csrf_cookie
def zone_control(request, zoneId):
    zone = get_object_or_404(Zone, pk=zoneId)
    active_request = RpiGpioRequest.objects.filter(status__in=[4], onDateTime__contains=date.today())
    return render(request, 
                'zone_control.html', 
                {
                'zone': zone,
                'active_request' : active_request,
                })

# main mobile browser based view for the irrigation website
# /mobile/mobile_index.html
@ensure_csrf_cookie
def mobile_index(request):
    zone_list = Zone.objects.filter(visible=True, enabled=True)
    active_request = RpiGpioRequest.objects.filter(status__in=[4], onDateTime__contains=date.today())
    return render(request,
                'mobile/mobile_index.html', 
                    {
                    'zone_list' : zone_list,
                    'active_request' : active_request,
                    })

# mobile browser single zone control view
# /mobile/mobile_zone_control.html
@ensure_csrf_cookie
def mobile_zone_control(request, zoneId):
    zone = get_object_or_404(Zone, pk=zoneId)
    active_request = RpiGpioRequest.objects.filter(status__in=[4], onDateTime__contains=date.today())
    return render(request, 
                'mobile/mobile_zone_control.html', 
                    {
                    'zone': zone,
                    'active_request' : active_request,
                    })

# web browser view invoked when the page for manually scheduling zone activities is loaded
# /manually_schedule.html
@ensure_csrf_cookie
def manually_schedule(request):
    zone_list = Zone.objects.filter(visible=True, enabled=True)
    todays_requests = RpiGpioRequest.objects.filter(status=1, onDateTime__contains=date.today())
    current_time_plus_5_minutes = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
    schedule_list = Schedule.objects.filter(enabled=True)     
    
    return render(request, 
        'manually_schedule.html',
            {
            'schedule_list': schedule_list, 
            'zone_list' : zone_list,
            'current_time_plus_5_minutes' : current_time_plus_5_minutes,
            'todays_requests' : todays_requests,
            })                               


# this is the command that is invoked when the user is on the manual schedule page and they click
# the "Schedule" button at the bottom of the page
def create_schedule(request):
    if request.method == 'POST':
      # 1st turn off all outputs
      turn_all_outputs_off()
        
      # 2nd cancel any upcoming scheduled requests for today
      cancel_all_current_requests()
      
      # need a list of the zones  
      zone_list = Zone.objects.filter(visible=True, enabled=True)
      # retrieve the start time from the form field "start_time" and tack on today's date
      startTime =  datetime.strptime(str(date.today()) + ' ' + request.POST['start_time'], "%Y-%m-%d %H:%M")
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
     # if there are any zone outputs currently ON, we should find an active RPiGPIORequest record
      # with a status of 4 which means "In Progress"
      active_requests = RpiGpioRequest.objects.filter(status__in=[4], onDateTime__contains=date.today())
      current_time_plus_1_minutes = (datetime.now() + timedelta(seconds=15)).strftime("%H:%M")
      newOffDateTime =  datetime.strptime(str(date.today()) + ' ' + current_time_plus_1_minutes, "%Y-%m-%d %H:%M")
      for rpiGpioRequest in active_requests:
          # override the offDateTime value for the "In Progress" request so that it is turned OFF 
          # by the Daemon
          rpiGpioRequest.offDateTime = newOffDateTime
          rpiGpioRequest.save()        


def cancel_all_current_requests():
    # cancel any upcoming scheduled requests for today
    # instantiate a Status of "Cancelled"
    cancelled_status = get_object_or_404(Status, pk=3)
    # retrieve all new requests
    todays_requests = RpiGpioRequest.objects.filter(status__in=[1], onDateTime__contains=date.today())

    # mark them as cancelled
    for rpiGpioRequest in todays_requests:
      rpiGpioRequest.status = cancelled_status
      rpiGpioRequest.save()


def turn_zone_on(zoneId):
    # read the Zone info from the database
    zone = get_object_or_404(Zone, pk=zoneId)
    rpiGpio = RpiGpio.objects.get(zone=zone)
    # special case - Zone corresponds to RpiGpio SYSTEM_ENABLED_GPIO
    if rpiGpio.gpioName == settings.SYSTEM_ENABLED_GPIO:
        zone = Turn24VACOn()
    else:
        ioid = int(rpiGpio.gpioNumber)
        zone = OutputCommand(ioid, zone, Commands.ON)
    return zone

def turn_zone_off(zoneId):
    # read the Zone info from the database
    zone = get_object_or_404(Zone, pk=zoneId)
    rpiGpio = RpiGpio.objects.get(zone=zone)

    # special case - Zone corresponds to RpiGpio SYSTEM_ENABLED_GPIO
    if rpiGpio.gpioName == settings.SYSTEM_ENABLED_GPIO:    
        zone = Turn24VACOff()
    else:
        ioid = int(rpiGpio.gpioNumber)
        zone = OutputCommand(ioid, zone, Commands.OFF)
    return zone

def rpi_gpio_request_cancel(request, id):
    rpiGpioOnRequest = get_object_or_404(RpiGpioRequest, pk=id)
    cancelled_status = get_object_or_404(Status, pk=3)
    # cancel the ON request
    rpiGpioOnRequest.status = cancelled_status
    rpiGpioOnRequest.save()
    return HttpResponseRedirect('/')

    
def rpi_gpio_request_cancel_all(request):
    # 1 is pending 4 is active
    rpiGpioOnRequests = RpiGpioRequest.objects.filter(Q(status=1) | Q(status=4))
    cancelled_status = get_object_or_404(Status, pk=3)
    # cancel the ON requests
    for rpiGpioOnRequest in rpiGpioOnRequests:
        rpiGpioOnRequest.status = cancelled_status
        rpiGpioOnRequest.save()
    return HttpResponseRedirect('/')


@require_http_methods(["GET"])
def get_schedule(request,  scheduleId):
    scheduleId = int(scheduleId)
    schedule = get_object_or_404(Schedule,  pk=scheduleId)
    queryset = schedule.irrigationschedule_set.all()
    serializer = IrrigationScheduleSerializer(queryset, many=True)
    
    return JsonResponse(serializer.data, safe=False)

# @require_http_methods(["GET"])
# def enable_system(request):
#     TurnIrrigationSystemActiveOn()
#     return HttpResponseRedirect('/')

# @require_http_methods(["GET"])
# def disable_system(request):
#     TurnIrrigationSystemActiveOff()
#     return HttpResponseRedirect('/')

# @require_http_methods(["GET"])
# def enable_24VAC(request):
#     Turn24VACOn()
#     return HttpResponseRedirect('/')

# @require_http_methods(["GET"])
# def disable_24VAC(request):
#     Turn24VACOff()
#     return HttpResponseRedirect('/')

@require_POST
def toggle_zone(request):
    response = {}
    json_data = json.loads(request.body.decode('utf-8'))
    zone_id = json_data['zoneId']

    # read the Zone info from the database
    try:
        zone = Zone.objects.get(pk=zone_id)

        # check to see if it is in an ON state
        if zone.is_on:
            zone = turn_zone_off(zone_id)
        else:   
            zone = turn_zone_on(zone_id)
        
        response['zone_id'] = zone.zoneId
        response['zone_name'] = zone.displayName
        response['zone_is_on'] = zone.is_on
        response["current_state"] = zone.currentState()
        response['success'] = True

    except Zone.DoesNotExist:
        response['error'] = "Zone {0} PK NOT FOUND".format(zone_id)
        response['success'] = False

    return JsonResponse(response)
