from django.conf import settings
from django.shortcuts import get_object_or_404
from sprinklesmart.models import RpiGpio, Zone, IrrigationSystem
from enum import Enum
import logging

logger = logging.getLogger(__name__)

if settings.GPIO_SIM_ENABLED:
    from RPiSim import GPIO
else:
    from RPi import GPIO

class Commands(Enum):
    OFF = 0
    ON = 1

def irrigation_system_enabled():
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    return irrigation_system.systemState

def output_rpi_gpio_command(rpiGpio, command):
    # need the gpioNumber and zone for the OutputCommand below
    ioid = int(rpiGpio.gpioNumber)
    zone = rpiGpio.zone
    zone = output_command(ioid, zone, command)
    return zone

def output_command(ioid, zone, command):
    # this function actually controls the RPi GPIO outputs
    # and it updates the zone table to indicate when a particular zone goes on or off
    # we can use the zone table to tell which outputs are off
    logger.debug("output_command ioid: {0} zone: {1} command: {2}".format(ioid, zone, command))
    try:
        if hasattr(GPIO, 'setwarnings'):
            GPIO.setwarnings(False)
        if hasattr(GPIO, 'setmode'):
            GPIO.setmode(GPIO.BOARD)
        if hasattr(GPIO, 'setup'):
            GPIO.setup(ioid, GPIO.OUT)
    
        if command == Commands.ON:
            if hasattr(GPIO, 'output'):
                GPIO.output(ioid, GPIO.HIGH)
            zone.is_on = True
            zone.save()
     
        if command == Commands.OFF:
            if hasattr(GPIO, 'output'):
                GPIO.output(ioid, GPIO.LOW)
            zone.is_on = False
            zone.save()
    except Exception as e:
        logger.error(e)
        logger.error("output_command ioid: {0} zone: {1} command: {2}".format(ioid, zone, command))
    finally:    
        return zone

def turn_all_zone_outputs_off():
    # this function iterates through all defined rpiGpio records
    # and invokes the OutputCommand to turn them all off
    rpi_gpios = RpiGpio.objects.filter(zone__visible=True)
    for rpi_gpio in rpi_gpios:
        output_rpi_gpio_command(rpi_gpio, Commands.OFF)
    
def turn_24_vac_off():
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    system_enabled_rpi_gpio = RpiGpio.objects.get(zone=irrigation_system.system_enabled_zone)
    zone = output_rpi_gpio_command(system_enabled_rpi_gpio, Commands.OFF)
    turn_all_zone_outputs_off()
    turn_irrigation_system_active_off()
    return zone
    
def turn_24_vac_on():
    # toggle the IrrigationSystem systemState
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    system_enabled_rpi_gpio = RpiGpio.objects.get(zone=irrigation_system.system_enabled_zone)
    zone = output_rpi_gpio_command(system_enabled_rpi_gpio, Commands.ON)
    return zone

def turn_irrigation_system_active_off():
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    irrigation_system_active_rpi_gpio = \
        RpiGpio.objects.get(zone=irrigation_system.valves_enabled_zone)
    zone = output_rpi_gpio_command(irrigation_system_active_rpi_gpio, Commands.OFF)
    return zone

def turn_irrigation_system_active_on():
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    if irrigation_system.systemState:
        irrigation_system_active_rpi_gpio = \
            RpiGpio.objects.get(zone=irrigation_system.valves_enabled_zone)
        zone = output_rpi_gpio_command(irrigation_system_active_rpi_gpio, Commands.ON)
    return zone



