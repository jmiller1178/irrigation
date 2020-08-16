from django.conf import settings
import logging
from urllib.parse import urljoin, urlencode
import urllib.request
import json
from datetime import datetime, date, timedelta
import time
from dateutil import parser
import uuid, urllib, urllib3
import hmac, hashlib
from base64 import b64encode
from yahoo_weather.weather import YahooWeather
from yahoo_weather.config.units import Unit


logger = logging.getLogger(__name__)

class WeatherAPI(object):
    def get_weather_from_yahoo(self):
        """
        Basic info
        """
        # url = settings.WEATHER_URL
        # method = 'GET'
        app_id = settings.WEATHER_APP_ID
        consumer_key = settings.WEATHER_CONSUMER_KEY
        consumer_secret = settings.WEATHER_CONSUMER_SECRET

        data = YahooWeather(APP_ID=app_id,
                     api_key=consumer_key,
                     api_secret=consumer_secret)

        data.get_yahoo_weather_by_city("hudsonville,mi", Unit.fahrenheit)
        
        return data

    # 7/9/2019 rewritten to use JSON service which requires OAUTH - stupid yahoo
    def read_current_weather_conditions(self):
        #response = self.get_weather_from_yahoo()

        #jsonResponse = json.loads(response.decode('utf-8'))
        weather_data = self.get_weather_from_yahoo()

        current_observation_date = weather_data.current_observation.pubDate

        city = weather_data.location.city
        state = weather_data.location.region
        title = "Conditions for {0},{1} at {2}".format(city, state, current_observation_date)
                
        weather_code = int(weather_data.current_observation.condition.code)
        
        temperature = weather_data.current_observation.condition.temperature
        uom = 'F'
        conditions = weather_data.current_observation.condition.text

        text = weather_data.forecasts[0].text
        high = weather_data.forecasts[0].high
        low = weather_data.forecasts[0].low
        reading_date = weather_data.forecasts[0].date
        day = weather_data.forecasts[0].day
        forecast1 = "{} {} {} High: {} {} Low: {} {}".format(day, reading_date, text, high, uom, low, uom)

        text = weather_data.forecasts[1].text
        high = weather_data.forecasts[1].high
        low = weather_data.forecasts[1].low
        reading_date = weather_data.forecasts[1].date
        day = weather_data.forecasts[1].day
        forecast2 = "{} {} {} High: {} {} Low: {} {}".format(day, reading_date, text, high, uom, low, uom)

        text = weather_data.forecasts[2].text
        high = weather_data.forecasts[2].high
        low = weather_data.forecasts[2].low
        reading_date = weather_data.forecasts[2].date
        day = weather_data.forecasts[2].day
        forecast3 = "{} {} {} High: {} {} Low: {} {}".format(day, reading_date, text, high, uom, low, uom)

        text = weather_data.forecasts[3].text
        high = weather_data.forecasts[3].high
        low = weather_data.forecasts[3].low
        reading_date = weather_data.forecasts[3].date
        day = weather_data.forecasts[3].day
        forecast4 = "{} {} {} High: {} {} Low: {} {}".format(day, reading_date, text, high, uom, low, uom)

        text = weather_data.forecasts[4].text
        high = weather_data.forecasts[4].high
        low = weather_data.forecasts[4].low
        reading_date = weather_data.forecasts[4].date
        day = weather_data.forecasts[4].day
        forecast5 = "{} {} {} High: {} {} Low: {} {}".format(day, reading_date, text, high, uom, low, uom)
        current_weather_conditions = {}
        current_weather_conditions['condition_date_time'] = current_observation_date
        current_weather_conditions['temperature'] = temperature
        current_weather_conditions['uom'] = uom
        current_weather_conditions['weather_code'] = weather_code
        current_weather_conditions['title'] = title
        current_weather_conditions['conditions'] = conditions
        
        forecast = {}
        forecast['day_1'] = forecast1
        forecast['day_2'] = forecast2
        forecast['day_3'] = forecast3
        forecast['day_4'] = forecast4
        forecast['day_5'] = forecast5
        current_weather_conditions['forecast'] = forecast
        
        return current_weather_conditions
        

