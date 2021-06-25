from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import urllib
from sprinklesmart.api.weather import WeatherAPI
from sprinklesmart import models
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    """
        Make a call to the yahoo weather API and record the 
        current weather conditions in the database
    """

    help = 'Record Current Weather Conditions'

    def internet_is_available(self):
        available = False
        try:
            response = urllib.request.urlopen(settings.INTERNET_CHECK_URL, timeout=1)
            available = True
        except urllib.error.URLError as err: 
            pass
            
        return available

    def handle(self, *args, **options):
        # check for internet availability before trying to read the weather conditions    
        if self.internet_is_available():
            weather_api = WeatherAPI()
            # weather_conditions = weather_api.read_current_weather_conditions()
            weather_conditions = weather_api.get_weather_from_openweathermap()
            
            title = weather_conditions['title']
            condition_date_time = weather_conditions['condition_date_time']
            temperature = weather_conditions['temperature']
            # uom = weather_conditions['uom']
            
            weather_code = weather_conditions['weather_code']
            condition_code = get_object_or_404(models.ConditionCode, pk=weather_code)

            # forecast = weather_conditions['forecast']
            # forecast_day_1 = forecast['day_1']
            # forecast_day_2 = forecast['day_2']
            # forecast_day_3 = forecast['day_3']
            # forecast_day_4 = forecast['day_4']
            # forecast_day_5 = forecast['day_5']
            
            weather_condition = models.WeatherCondition()
            
            weather_condition.title = title
            weather_condition.conditionDateTime = condition_date_time
            weather_condition.temperature = temperature
            # unitOfMeasure = uom
            weather_condition.conditionCode = condition_code
            # weather_condition.forecastDay1 = forecast_day_1
            # weather_condition.forecastDay2 = forecast_day_2
            # weather_condition.forecastDay3 = forecast_day_3
            # weather_condition.forecastDay4 = forecast_day_4
            #  weather_condition.forecastDay5 = forecast_day_5
            
            weather_condition.save()
            
