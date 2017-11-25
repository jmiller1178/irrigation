from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import urllib2
from sprinklesmart.api.weather import WeatherAPI
from django.shortcuts import get_object_or_404
import pytz
from datetime import datetime, date, timedelta
from sprinklesmart.models import RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition

class Command(BaseCommand):
    help = 'Schedule Irrigation Controller Events'
    
    def handle(self, *args, **options):
        # Let's start by checking if ANYTHING is scheduled for today because, if there is, then we shouldn't
        # have to execute any of the code below, right??
        requests = RpiGpioRequest.objects.filter(status__in=[1,4], onDateTime__contains=date.today())
        
        if requests.count() ==0:
            # there is nothing scheduled for today so do the scheduling process
            
            # look for active schedule(s) with a start time within the next hour
            enabled_schedules = Schedule.objects.filter(enabled=True)
            eastern = pytz.timezone('US/Eastern')
            sprinkle_smart_multiplier = self.get_sprinkle_smart_multiplier()
            
            # retrieve IrrigationSchedule records for this day of the week and for the above Schedule 
            current_time = datetime.now(eastern)
            
            # find the WeekDay object for today
            week_day = get_object_or_404(WeekDay, weekDay=current_time.weekday())
            pending_status = get_object_or_404(Status, pk=1)
            
            for schedule in enabled_schedules:
                schedule_time=datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute, tzinfo=eastern)
                if schedule_time > current_time:
                    delta_time=schedule_time-current_time
                    minutes_in_future = (delta_time.seconds * sprinkle_smart_multiplier) / 60
                    
                    if minutes_in_future < 60:
                        # we're less than an hour away from scheduled start time so need to stup the RpiGpioRequests per that schedule
                        irrigation_schedules = schedule.irrigationschedule_set.filter(weekDays=week_day).order_by('sortOrder')
                        zone_start_time = datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute,tzinfo=pytz.UTC)
                        
                        for irrigation_schedule in irrigation_schedules:
                            # create RpiGpioRequest records for today
                            # there should only be one rpiGpio per zone but it is a set so iterate anyway
                            rpigpios = irrigation_schedule.zone.rpigpio_set.all()
                            
                            for rpigpio in rpigpios:            
                                        
                                scheduled_request = RpiGpioRequest()
                                scheduled_request.rpiGpio=rpigpio
                                scheduled_request.onDateTime = zone_start_time
                                
                                duration_seconds = irrigation_schedule.duration * 60
                                zone_end_time = zone_start_time + timedelta(0, duration_seconds)
                                
                                scheduled_request.offDateTime = zone_end_time
                                scheduled_request.status = pending_status
                                scheduled_request.durationMultiplier = sprinkle_smart_multiplier
                                scheduled_request.save()
                                
                                zone_start_time = zone_end_time
    
    
    def get_sprinkle_smart_multiplier(self):
        multiplier = 1.0
        
        weather_conditions=WeatherCondition.objects.filter(conditionDateTime__gt=datetime.now(pytz.UTC)-timedelta(days=2))
        total_count = weather_conditions.count()
        rain_count = 0
        for weather_condition in weather_conditions:
            if weather_condition.conditionCode.IsRaining():
                rain_count = rain_count + 1
                
        multiplier = 1.0 - rain_count / total_count

        return multiplier
