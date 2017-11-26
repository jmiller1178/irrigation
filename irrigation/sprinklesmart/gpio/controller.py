from django.shortcuts import get_object_or_404
import RPi.GPIO as GPIO
from sprinklesmart.models import RpiGpio, Zone
from enum import Enum

class Commands(Enum):
    OFF = 0
    ON = 1

def OutputCommand(ioid, zone, command):
    # this function actually controls the RPi GPIO outputs
    # and it updates the zone table to indicate when a particular zone goes on or off
    # we can use the zone table to tell which outputs are off
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(ioid, GPIO.OUT)
    
    if command == Commands.ON:
        GPIO.output(ioid, GPIO.HIGH)
        zone.is_on = True
        zone.save()

    if command == Commands.OFF:
        GPIO.output(ioid, GPIO.LOW)
        zone.is_on = False
        zone.save()


def TurnAllOutputsOff():
    # this function iterates through all defined rpiGpio records
    # and invokes the OutputCommand to turn them all off
    rpi_gpios = RpiGpio.objects.all()
    for rpi_gpio in rpi_gpios:
        # need to fulfill the request
        ioid = rpi_gpio.gpioNumber
        zone = rpi_gpio.zone
        OutputCommand(ioid, zone, Commands.OFF)
    
