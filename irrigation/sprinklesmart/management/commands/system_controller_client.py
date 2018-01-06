from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from datetime import datetime, date, timedelta
from sprinklesmart.models import RpiGpio, RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition, IrrigationSystem
from sprinklesmart.gpio.controller import OutputCommand, Commands, TurnAllOutputsOff
from django.db.models import Q, Min
import logging
import socket
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'System Controller Client'
    
    def handle(self, *args, **options):
		rpi_gpio = RpiGpio.objects.get(gpioName='GPIO27')
		ioid = rpi_gpio.gpioNumber
		zone = rpi_gpio.zone
		OutputCommand(ioid, zone, Commands.OFF)
		
		while True:
			s = socket.socket()
			host = '192.168.1.127'
			port = 7651
			try:
				s.connect((host, port))
				s.send("hello world")
				OutputCommand(ioid, zone, Commands.ON)
				print "the message has been sent"
			
				time.sleep(1)
				
			except:
				OutputCommand(ioid, zone, Commands.OFF)				
