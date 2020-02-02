from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from datetime import datetime
from sprinklesmart.models import *
from sprinklesmart.gpio.controller import *
from django.db.models import Q
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process RPi GPIO Requests'
    
    def handle(self, *args, **options):
        # logger.debug("process_rpigpio_request invoked")
        irrigation_system = get_object_or_404(IrrigationSystem, pk=1)

        pending_status = get_object_or_404(Status, pk=1) # 1 is pending
        complete_status = get_object_or_404(Status, pk=2) # 2 is complete
        cancel_status = get_object_or_404(Status, pk=3) # 3 is cancel
        active_status = get_object_or_404(Status, pk=4) # 4 is active

        # get the current weatherconditions
        current_weather = WeatherCondition.objects.order_by('-id')[0]

        # read the IrrigationSystem.systemState
        
        system_enabled = irrigation_system.systemState
        
        # if it is raining or the irrigation system is disabled
        if current_weather.conditionCode.IsRaining() or not system_enabled:
            # turn off 24VAC
            turn_24_vac_off()
            # turn off all other outputs
            turn_all_outputs_off()
            # turn off the indicator that the system is active - this is the blue LED
            turn_irrigation_system_active_off()
        else:
            # otherwise
            # turn on 24VAC
            Turn24VACOn()
        
        twentyfour_vac_enabled = irrigation_system.system_enabled_zone.is_on

        if system_enabled and twentyfour_vac_enabled:
            # system is completely enabled
            # logger.debug("Irrigation System is Enabled")
            
            current_time = datetime.now()
            match_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, second=0, microsecond=0)
                        
            # are there any active requests whith the off time equal to now (to the minute)
            active_requests = RpiGpioRequest.objects.filter(status=active_status, offDateTime=match_time)
            # logger.debug("active requests count {0}".format(active_requests.count()))
            # if there are turn off the output
            if active_requests.count() > 0:
                for active_request in active_requests:
                    outputRpiGpioCommand(active_request.rpiGpio, Commands.OFF)
                    active_request.status = complete_status
                    active_request.save()
                    TurnIrrigationSystemActiveOff()
                    
            # are there any pending requests with the on time equal to now (to the minute)
            pending_requests = RpiGpioRequest.objects.filter(status=pending_status, onDateTime=match_time)
            # logger.debug("pending_requests count {0}".format(pending_requests.count()))

            # if there are turn on the output
            if pending_requests.count() > 0:
                for pending_request in pending_requests:
                    outputRpiGpioCommand(pending_request.rpiGpio, Commands.ON)
                    pending_request.status = active_status
                    pending_request.save()
                    TurnIrrigationSystemActiveOn()
                    
            else:
                pending_request = RpiGpioRequest.objects.filter(status=pending_status).order_by('onDateTime').first()
                # logger.debug("next pending_request {0}".format(pending_request))
        else:
            # logger.debug("Irrigation System is Disabled")
            TurnAllOutputsOff()
            TurnIrrigationSystemActiveOff() 
            # cancel all requests which are active or pending
            open_requests = RpiGpioRequest.objects.filter(Q(status=active_status) | Q(status=pending_status))
            if open_requests.count() > 0:
                for request in open_requests:
                    request.status = cancel_status
                    request.save()
                    
