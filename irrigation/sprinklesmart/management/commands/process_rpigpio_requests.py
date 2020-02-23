from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.shortcuts import get_object_or_404
from sprinklesmart.models import RpiGpioRequest, IrrigationSystem, Status, WeatherCondition
from sprinklesmart.gpio.controller import *
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process RPi GPIO Requests'
    
    def handle(self, *args, **options):
        irrigation_system = IrrigationSystem.objects.get(pk=1)

        if irrigation_system.system_mode.manual_mode:
            # need to cancel any outstanding RPiGPIO requests
            requests = RpiGpioRequest.pending_requests.all()
            cancelled_status = get_object_or_404(Status, pk=3) # 3 is cancelled
            for request in requests:
                request.status = cancelled_status
                request.save()
            # turn off the indicator that we have valves enabled (aka Blue LED)
            turn_irrigation_system_active_off()

        # are we in automatic mode and the system enabled
        if irrigation_system.system_mode.automatic_mode and\
            irrigation_system.systemState:

            # pending_status = get_object_or_404(Status, pk=1) # 1 is pending
            complete_status = get_object_or_404(Status, pk=2) # 2 is complete
            active_status = get_object_or_404(Status, pk=4) # 4 is active

            # get the current weatherconditions - used for determining if it is raining
            current_weather = WeatherCondition.objects.order_by('-id')[0]

            # if it is raining or the irrigation system is disabled
            if current_weather.conditionCode.IsRaining:
                # turn off 24VAC
                turn_24_vac_off()
            else:
                # turn on 24VAC
                turn_24_vac_on()

            # are there any active requests whith the off time equal to now (to the minute)
            off_requests = RpiGpioRequest.off_requests.all()

            # if there are turn off the output
            if off_requests.count() > 0:
                for off_request in off_requests:
                    output_rpi_gpio_command(off_request.rpiGpio, Commands.OFF)
                    off_request.status = complete_status
                    off_request.save()
                    
            # are there any pending requests with the on time equal to now (to the minute)
            pending_on_requests = RpiGpioRequest.pending_requests.all()

            # if there are turn on the output
            if pending_on_requests.count() > 0:
                # turn on the indicator that we have valves enabled (aka Blue LED)
                turn_irrigation_system_active_on()
                for pending_on_request in pending_on_requests:
                    output_rpi_gpio_command(pending_on_request.rpiGpio, Commands.ON)
                    pending_on_request.status = active_status
                    pending_on_request.save()
            
            # are there any pending or active requests with the on time equal to now (to the minute)
            pending_or_active_requests = RpiGpioRequest.pending_or_active_requests.all()
            if pending_or_active_requests.count() == 0:
                # turn off the indicator that we have valves enabled (aka Blue LED)
                turn_irrigation_system_active_off()

            # active requests need to be saved so they trigger UI update
            active_requests = RpiGpioRequest.active_requests.all()
            for active_request in active_requests:
                active_request.save()
             
