from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from datetime import datetime, date, timedelta
from sprinklesmart.models import RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition, IrrigationSystem
from sprinklesmart.gpio.controller import OutputCommand, Commands, TurnAllOutputsOff
from django.db.models import Q, Min
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process RPi GPIO Requests'
    
    def handle(self, *args, **options):
		TurnAllOutputsOff()
                   
