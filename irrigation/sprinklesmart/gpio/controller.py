from sprinklesmart.models import RpiGpio, Zone
from enum import Enum
from django.conf import settings
from django.shortcuts import get_object_or_404

if settings.GPIO_SIM_ENABLED:
    from RPiSim import GPIO
else:
    from RPi import GPIO

class Commands(Enum):
    OFF = 0
    ON = 1
    
def OutputRpiGpioCommand(rpiGpio, command):
    # need the gpioNumber and zone for the OutputCommand below
    ioid = rpiGpio.gpioNumber
    zone = rpiGpio.zone
    OutputCommand(ioid, zone, command)

def OutputCommand(ioid, zone, command):
    # this function actually controls the RPi GPIO outputs
    # and it updates the zone table to indicate when a particular zone goes on or off
    # we can use the zone table to tell which outputs are off
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

def TurnAllOutputsOff():
    # this function iterates through all defined rpiGpio records
    # and invokes the OutputCommand to turn them all off
    rpi_gpios = RpiGpio.objects.filter(zone__visible=True)
    for rpi_gpio in rpi_gpios:
        OutputRpiGpioCommand(rpi_gpio, Commands.OFF)
    
def Turn24VACOff():
    # this is the GPIO which enables 24VAC to the valve control relays
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    OutputRpiGpioCommand(system_enabled_rpi_gpio, Commands.OFF)
    
def Turn24VACOn():
    # this is the GPIO which enables 24VAC to the valve control relays	
    system_enabled_rpi_gpio = RpiGpio.objects.get(gpioName=settings.SYSTEM_ENABLED_GPIO)
    OutputRpiGpioCommand(system_enabled_rpi_gpio, Commands.ON)
    
def TurnIrrigationSystemActiveOff():
    irrigation_system_active_rpi_gpio = \
        RpiGpio.objects.get(gpioName=settings.IRRIGATION_ACTIVE_GPIO)
    ioid = irrigation_system_active_rpi_gpio.gpioNumber
    zone = irrigation_system_active_rpi_gpio.zone
    
    if hasattr(GPIO, 'setwarnings'):
        GPIO.setwarnings(False)

    if hasattr(GPIO,'setmode'):
        GPIO.setmode(GPIO.BOARD)

    if hasattr(GPIO,'setup'):
        GPIO.setup(ioid, GPIO.OUT)
    
    if hasattr(GPIO, 'output'):
        GPIO.output(ioid, GPIO.LOW)
    zone.is_on = True
    zone.save()
    TurnAllOutputsOff()

def TurnIrrigationSystemActiveOn():
    irrigation_system_active_rpi_gpio = \
        RpiGpio.objects.get(gpioName=settings.IRRIGATION_ACTIVE_GPIO)
    ioid = irrigation_system_active_rpi_gpio.gpioNumber
    zone = irrigation_system_active_rpi_gpio.zone

    if hasattr(GPIO, 'setwarnings'):
        GPIO.setwarnings(False)

    if hasattr(GPIO,'setmode'):
        GPIO.setmode(GPIO.BOARD)

    if hasattr(GPIO,'setup'):
        GPIO.setup(ioid, GPIO.OUT)
    if hasattr(GPIO, 'output'):
        GPIO.output(ioid, GPIO.HIGH)
    zone.is_on = True
    zone.save()

