from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from datetime import datetime, date, timedelta
from sprinklesmart.models import RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition, IrrigationSystem
from sprinklesmart.gpio.controller import OutputCommand, Commands, TurnAllOutputsOff
from django.db.models import Q, Min
import logging
import sys
import socket

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'System Controller Server'
    
    def handle(self, *args, **options):
		s = socket.socket()
		host = '' #socket.gethostname()
		port = 7651
		s.bind((host,port))

		s.listen(5)
		while True:
			c, addr = s.accept()
			print("Connection accepted from " + addr[0])
			# print addr[0]
			c.send("Server approved connection\n")
			print repr(addr[0]) + ": " + c.recv(1026)
			c.close()

