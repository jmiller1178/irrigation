from django.core.management.base import BaseCommand
from sprinklesmart.models import RpiGpioRequest, Schedule, WeekDay, Status, WeatherCondition, IrrigationSystem
from sprinklesmart.gpio.controller import turn_all_zone_outputs_off
from django.db.models import Q, Min
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process RPi GPIO Requests'
    
    def handle(self, *args, **options):
      turn_all_zone_outputs_off()
      