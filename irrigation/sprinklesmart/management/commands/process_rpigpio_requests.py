from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
import pytz
from datetime import datetime, date, timedelta
from sprinklesmart.models import RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition, IrrigationSystem
from sprinklesmart.gpio.controller import OutputCommand, Commands, TurnAllOutputsOff
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process RPi GPIO Requests'
    
    def handle(self, *args, **options):
        irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
        logger.debug("process_rpigpio_request invoked")
        
        if irrigation_system.systemState == True: # system is enabled
            logger.debug("Irrigation System is Enabled")
            active_status = get_object_or_404(Status, pk=4) # 4 is active
            pending_status = get_object_or_404(Status, pk=1) # 1 is pending
            complete_status = get_object_or_404(Status, pk=2) # 2 is complete
            eastern = pytz.timezone('US/Eastern')
            current_time = datetime.now(eastern)
            
            match_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, second=0, microsecond=0, tzinfo=pytz.UTC)
            
            # are there any active requests whith the off time equal to now (to the minute)
            active_requests = RpiGpioRequest.objects.filter(status=active_status, offDateTime=match_time)
            # if there are turn off the output
            if active_requests.count() > 0:
                for active_request in active_requests:
                    ioid = active_request.rpiGpio.gpioNumber
                    zone = active_request.rpiGpio.zone
                    OutputCommand(ioid, zone, Commands.OFF)
                    active_request.status = complete_status
                    active_request.save()
                    
            # are there any pending requests with the on time equal to now (to the minute)
            pending_requests = RpiGpioRequest.objects.filter(status=pending_status, onDateTime=match_time)
            # if there are turn on the output
            if pending_requests.count() > 0:
                for pending_request in pending_requests:
                    ioid = pending_request.rpiGpio.gpioNumber
                    zone = pending_request.rpiGpio.zone
                    OutputCommand(ioid, zone, Commands.ON)
                    pending_request.status = active_status
                    pending_request.save()
        else:
            logger.debug("Irrigation System is Disabled")
            TurnAllOutputsOff()
            # cancel all requests which are active or pending
            active_status = get_object_or_404(Status, pk=4) # 4 is active
            pending_status = get_object_or_404(Status, pk=1) # 1 is pending
            cancel_status = get_object_or_404(Status, pk=3) # 3 is cancel
            open_requests = RpiGpioRequest.objects.filter(Q(status=active_status) | Q(status=pending_status))
            if open_requests.count() > 0:
                for request in open_requests:
                    print "open requests found"
                    request.status = cancel_status
                    request.save()
                    
