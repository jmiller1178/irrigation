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
    # this is the GPIO which enables the entire system
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    zone = output_rpi_gpio_command(system_enabled_rpi_gpio, Commands.OFF)
    # toggle the IrrigationSystem systemState
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    irrigation_system.systemState = False
    irrigation_system.save()
    # turn off everything - all the zones that is
    turn_all_zone_outputs_off()
    # turn off the irrigation system active (BLUE LED) too
    turn_irrigation_system_active_off()
    return zone
    
def turn_24_vac_on():
    # toggle the IrrigationSystem systemState
    irrigation_system = get_object_or_404(IrrigationSystem, pk=1)
    irrigation_system.systemState = True
    irrigation_system.save()

    # this is the GPIO which enables 24VAC to the valve control relays
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    zone = output_rpi_gpio_command(system_enabled_rpi_gpio, Commands.ON)
    return zone

def turn_irrigation_system_active_off():
    # get the state of the blue LED output - this is just an indicator that the system is active
    irrigation_system_active_rpi_gpio = \
        RpiGpio.objects.get(gpioName=settings.IRRIGATION_ACTIVE_GPIO)
    ioid = int(irrigation_system_active_rpi_gpio.gpioNumber)
    zone = irrigation_system_active_rpi_gpio.zone

    if hasattr(GPIO, 'setwarnings'):
        GPIO.setwarnings(False)

    if hasattr(GPIO, 'setmode'):
        GPIO.setmode(GPIO.BOARD)

    if hasattr(GPIO, 'setup'):
        GPIO.setup(ioid, GPIO.OUT)
    
    if hasattr(GPIO, 'output'):
        GPIO.output(ioid, GPIO.LOW)
    zone.is_on = False
    zone.save()
    turn_all_zone_outputs_off()
    return zone

def turn_irrigation_system_active_on():
    # get the state of the blue LED output - this is just an indicator that the system is active
    irrigation_system_active_rpi_gpio = \
        RpiGpio.objects.get(gpioName=settings.IRRIGATION_ACTIVE_GPIO)
    ioid = int(irrigation_system_active_rpi_gpio.gpioNumber)
    zone = irrigation_system_active_rpi_gpio.zone

    if hasattr(GPIO, 'setwarnings'):
        GPIO.setwarnings(False)

    if hasattr(GPIO, 'setmode'):
        GPIO.setmode(GPIO.BOARD)

    if hasattr(GPIO, 'setup'):
        GPIO.setup(ioid, GPIO.OUT)
    if hasattr(GPIO, 'output'):
        GPIO.output(ioid, GPIO.HIGH)
    zone.is_on = True
    zone.save()
    return zone



