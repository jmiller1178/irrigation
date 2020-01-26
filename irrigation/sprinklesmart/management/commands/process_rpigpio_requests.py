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
        
        pending_status = get_object_or_404(Status, pk=1) # 1 is pending
        complete_status = get_object_or_404(Status, pk=2) # 2 is complete
        cancel_status = get_object_or_404(Status, pk=3) # 3 is cancel
        active_status = get_object_or_404(Status, pk=4) # 4 is active

        # this is the GPIO which enables 24VAC to the valve control relays
        system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)

        # get the current weatherconditions
        current_weather = WeatherCondition.objects.order_by('-id')[0]

        # read the IrrigationSystem.systemState
        irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
        system_enabled = irrigation_system.systemState
        
        # if it is raining or the irrigation system is disabled
        if current_weather.conditionCode.IsRaining() or not system_enabled:
            # turn off 24VAC
            Turn24VACOff()
            # turn off all other outputs
            TurnAllOutputsOff()
        else:
            # otherwise
            # turn on 24VAC
            Turn24VACOn()
        
        twentyfour_vac_enabled = system_enabled_rpi_gpio.zone.is_on

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
                    OutputRpiGpioCommand(active_request.rpiGpio, Commands.OFF)
                    active_request.status = complete_status
                    active_request.save()
                    TurnIrrigationSystemActiveOff()
                    
            # are there any pending requests with the on time equal to now (to the minute)
            pending_requests = RpiGpioRequest.objects.filter(status=pending_status, onDateTime=match_time)
            # logger.debug("pending_requests count {0}".format(pending_requests.count()))

            # if there are turn on the output
            if pending_requests.count() > 0:
                for pending_request in pending_requests:
                    OutputRpiGpioCommand(pending_request.rpiGpio, Commands.ON)
                    pending_request.status = active_status
                    pending_request.save()
                    TurnIrrigationSystemActiveOn()
                    
            else:
                pending_request = RpiGpioRequest.objects.filter(status=pending_status).order_by('onDateTime').first()
                # logger.debug("next pending_request {0}".format(pending_request))
        else:
            # logger.debug("Irrigation System is Disabled")
            TurnAllOutputsOff()
            # cancel all requests which are active or pending
            open_requests = RpiGpioRequest.objects.filter(Q(status=active_status) | Q(status=pending_status))
            if open_requests.count() > 0:
                for request in open_requests:
                    request.status = cancel_status
                    request.save()
                    
