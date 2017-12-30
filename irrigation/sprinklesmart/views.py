# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import  reverse
from django.db.models import Q
from models import RpiGpioRequest
from models import RpiGpio
from models import Zone
from models import Status
from models import WeatherCondition
from models import IrrigationSystem
from django.template import Context, loader,  RequestContext
from datetime import datetime, date, timedelta
from django.conf import settings
from django.db.models import Max
from os.path import exists 
from django.views.decorators.csrf import ensure_csrf_cookie
from sprinklesmart.gpio.controller import OutputCommand, Commands

# main browser based view for the irrigation website
# /index.html
def index(request):
	pid_file_name='/var/run/IrrigationController.pid'

	if exists(pid_file_name):
		daemon_status = "ON"
	else:
		daemon_status = "OFF"

	zone_list = Zone.objects.all()
	current_date = datetime.now()
	todays_requests = RpiGpioRequest.objects.filter(status__in=[1,4], onDateTime__contains=date.today())

	if WeatherCondition.objects.all().count() > 0:
		current_weather = WeatherCondition.objects.order_by('-id')[0]
	else:
		current_weather = None
		
	if IrrigationSystem.objects.all().count() > 0:
		system_enabled = IrrigationSystem.objects.order_by('-id')[0]
	else:
		system_enabled = False
		
	return render(request, 
				'index.html', 
				{
				  'zone_list' : zone_list,
				  'current_date' : current_date,
				  'todays_requests' : todays_requests,
				  'current_weather' : current_weather,
				  'daemon_status' : daemon_status,
				  'system_enabled' : system_enabled
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
    zone_list = Zone.objects.all()
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
    zone_list = Zone.objects.all()
    todays_requests = RpiGpioRequest.objects.filter(status=1, onDateTime__contains=date.today())
    current_time_plus_5_minutes = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
                               
    return render(request, 
		'manually_schedule.html',
		{
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
      zone_list = Zone.objects.all()
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
	ioid = rpiGpio.gpioNumber

	OutputCommand(ioid, zone, Commands.ON)


def turn_zone_off(zoneId):
	# read the Zone info from the database
	zone = get_object_or_404(Zone, pk=zoneId)
	rpiGpio = RpiGpio.objects.get(zone=zone)
	ioid = rpiGpio.gpioNumber

	OutputCommand(ioid, zone, Commands.OFF)


def zone_toggle(request, zoneId):
    # read the Zone info from the database
    zone = get_object_or_404(Zone, pk=zoneId)

    # check to see if it is in an ON state
    if zone.currentState() == "ON":
		turn_zone_off(zoneId)
       
    # check to see if it is in an OFF state
    if zone.currentState() == "OFF":    
        # it is OFF so create an RpiGpioRequest record to have it turned on
        if request.method == 'POST':
            #cancel_all_current_requests()
            #duration = int(request.POST['duration'])
            turn_zone_on(zoneId)
 

    return HttpResponseRedirect('/')


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
