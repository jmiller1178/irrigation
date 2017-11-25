from django.conf import settings
import logging
from urlparse import urljoin
import requests
from urllib import urlencode, urlopen
import json
from datetime import datetime, date, timedelta
import time
from dateutil import parser
import pytz
from django.utils import timezone

logger = logging.getLogger(__name__)

class WeatherAPI(object):
	
	# 7/7/2016 JRM - use yahoo yql to query weather since pywapi doesn't work (stupid yahoo.com)
	def read_current_weather_conditions(self):
		baseurl = settings.WEATHER_URL

		yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='hudsonville, mi')"

		yql_url = baseurl + urlencode({'q':yql_query}) + "&format=json"

		response = urlopen(yql_url).read()
		jsonResponse = json.loads(response.decode('utf-8'))
										 
		title = jsonResponse['query']['results']['channel']['item']['title']
	
		condition_time_stamp = jsonResponse['query']['results']['channel']['item']['condition']['date']
		condition_date_time = timezone.make_aware(parser.parse(condition_time_stamp), pytz.UTC)
				
		weather_code = int(jsonResponse['query']['results']['channel']['item']['condition']['code'])
		
		temperature = jsonResponse['query']['results']['channel']['item']['condition']['temp']
		uom = jsonResponse['query']['results']['channel']['units']['temperature']
		conditions = jsonResponse['query']['results']['channel']['item']['condition']['text']

		text = jsonResponse['query']['results']['channel']['item']['forecast'][1]['text']
		high = jsonResponse['query']['results']['channel']['item']['forecast'][1]['high']
		low = jsonResponse['query']['results']['channel']['item']['forecast'][1]['low']
		date = jsonResponse['query']['results']['channel']['item']['forecast'][1]['date']
		day = jsonResponse['query']['results']['channel']['item']['forecast'][1]['day']
		forecast1 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['query']['results']['channel']['item']['forecast'][2]['text']
		high = jsonResponse['query']['results']['channel']['item']['forecast'][2]['high']
		low = jsonResponse['query']['results']['channel']['item']['forecast'][2]['low']
		date = jsonResponse['query']['results']['channel']['item']['forecast'][2]['date']
		day = jsonResponse['query']['results']['channel']['item']['forecast'][2]['day']
		forecast2 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['query']['results']['channel']['item']['forecast'][3]['text']
		high = jsonResponse['query']['results']['channel']['item']['forecast'][3]['high']
		low = jsonResponse['query']['results']['channel']['item']['forecast'][3]['low']
		date = jsonResponse['query']['results']['channel']['item']['forecast'][3]['date']
		day = jsonResponse['query']['results']['channel']['item']['forecast'][3]['day']
		forecast3 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['query']['results']['channel']['item']['forecast'][4]['text']
		high = jsonResponse['query']['results']['channel']['item']['forecast'][4]['high']
		low = jsonResponse['query']['results']['channel']['item']['forecast'][4]['low']
		date = jsonResponse['query']['results']['channel']['item']['forecast'][4]['date']
		day = jsonResponse['query']['results']['channel']['item']['forecast'][4]['day']
		forecast4 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['query']['results']['channel']['item']['forecast'][5]['text']
		high = jsonResponse['query']['results']['channel']['item']['forecast'][5]['high']
		low = jsonResponse['query']['results']['channel']['item']['forecast'][5]['low']
		date = jsonResponse['query']['results']['channel']['item']['forecast'][5]['date']
		day = jsonResponse['query']['results']['channel']['item']['forecast'][5]['day']
		forecast5 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)
		
		
		current_weather_conditions = {}
		current_weather_conditions['condition_date_time'] = condition_date_time
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
		
    
