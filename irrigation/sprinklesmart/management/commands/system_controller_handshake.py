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
	help = 'System Controller Handshake'
	
	
	def handle(self, *args, **options):
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind(('localhost', 7651))
		serversocket.listen(5) # become a server socket, maximum 5 connections

		while True:
			connection, address = serversocket.accept()
			buf = connection.recv(64)
			if len(buf) > 0:
				print (buf)
			break
		
