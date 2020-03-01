from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, date, timedelta
from sprinklesmart.models import (IrrigationSystem, RpiGpioRequest, Schedule,
                                WeekDay, Status, WeatherCondition)
from sprinklesmart.api.weather import WeatherAPI

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
        look for any upcoming irrigation schedules and
        create the rpigpio requests in the database
    """

    help = 'Schedule Irrigation Controller Events'
    
    def handle(self, *args, **options):
        irrigation_system = IrrigationSystem.objects.get(pk=1)
        
        # are we in automatic mode and the system enabled
        if irrigation_system.system_mode.automatic_mode and\
            irrigation_system.systemState:

            # active_status = get_object_or_404(Status, pk=4) # 4 is active
            pending_status = get_object_or_404(Status, pk=1) # 1 is pending

            # Let's start by checking if ANYTHING is scheduled for today because, if there is, then we shouldn't
            # have to execute any of the code below, right??
            requests = RpiGpioRequest.pending_requests.all()
        
            if requests.count() == 0:
                weather_api = WeatherAPI()
                # there is nothing scheduled for today so do the scheduling process
            
                # look for active schedule(s) with a start time within the next hour
                enabled_schedules = Schedule.objects.filter(enabled=True)
                sprinkle_smart_multiplier = weather_api.get_sprinkle_smart_multiplier()
            
                # retrieve IrrigationSchedule records for this day of the week and for the above Schedule
                current_time = datetime.now()

                # find the WeekDay object for today
                week_day = get_object_or_404(WeekDay, weekDay=current_time.weekday())
            
                for schedule in enabled_schedules:
                
                    schedule_time = datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute)
                    if schedule_time > current_time:
                        delta_time = schedule_time-current_time
                        minutes_in_future = delta_time.seconds / 60
                    
                        if minutes_in_future < 480:
                            # we're less than 8 hours away from scheduled start time so need to stup the RpiGpioRequests per that schedule
                            irrigation_schedules = schedule.irrigationschedule_set.filter(weekDays=week_day).order_by('sortOrder')
                            zone_start_time = datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute)

                            for irrigation_schedule in irrigation_schedules:
                                # create RpiGpioRequest records for today
                                # there should only be one rpiGpio per zone but it is a set so iterate anyway
                                rpigpios = irrigation_schedule.zone.rpigpio_set.all()
                            
                                for rpigpio in rpigpios:            
                                    scheduled_request = RpiGpioRequest()
                                    scheduled_request.rpiGpio = rpigpio
                                    scheduled_request.onDateTime = zone_start_time
                                    
                                    duration_seconds = irrigation_schedule.duration * sprinkle_smart_multiplier * 60
                                    zone_end_time = zone_start_time + timedelta(0, duration_seconds)
                                    
                                    scheduled_request.offDateTime = zone_end_time
                                    scheduled_request.status = pending_status
                                    scheduled_request.durationMultiplier = sprinkle_smart_multiplier
                                    scheduled_request.save()
                                    zone_start_time = zone_end_time
    
    
