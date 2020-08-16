from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, date, timedelta
from sprinklesmart.models import (IrrigationSystem, RpiGpioRequest, Schedule,
                                WeekDay, Status, WeatherCondition)
from sprinklesmart.api.weather import WeatherAPI

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
        look for any upcoming irrigation schedules and
        create the rpigpio requests in the database
    """

    help = 'Schedule Irrigation Controller Events'
    
    def handle(self, *args, **options):
        irrigation_system = IrrigationSystem.objects.get(pk=1)
        irrigation_system.schedule_irrigation_controller()        
    
    
