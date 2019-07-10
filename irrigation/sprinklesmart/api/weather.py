from django.conf import settings
import logging
from urlparse import urljoin
import requests
from urllib import urlencode, urlopen
import json
from datetime import datetime, date, timedelta
import time
from dateutil import parser
import uuid, urllib, urllib2
import hmac, hashlib
from base64 import b64encode

logger = logging.getLogger(__name__)

class WeatherAPI(object):
	def get_weather_from_yahoo(self):
		"""
		Basic info
		"""
		url = settings.WEATHER_URL
		method = 'GET'
		app_id = settings.WEATHER_APP_ID
		consumer_key = settings.WEATHER_CONSUMER_KEY
		consumer_secret = settings.WEATHER_CONSUMER_SECRET

		concat = '&'
		query = {'location': 'hudsonville,mi', 'format': 'json'}
		oauth = {
		    'oauth_consumer_key': consumer_key,
		    'oauth_nonce': uuid.uuid4().hex,
		    'oauth_signature_method': 'HMAC-SHA1',
		    'oauth_timestamp': str(int(time.time())),
		    'oauth_version': '1.0'
		}

		"""
		Prepare signature string (merge all params and SORT them)
		"""
		merged_params = query.copy()
		merged_params.update(oauth)
		sorted_params = [k + '=' + urllib.quote(merged_params[k], safe='') for k in sorted(merged_params.keys())]
		signature_base_str =  method + concat + urllib.quote(url, safe='') + concat + urllib.quote(concat.join(sorted_params), safe='')

		"""
		Generate signature
		"""
		composite_key = urllib.quote(consumer_secret, safe='') + concat
		oauth_signature = b64encode(hmac.new(composite_key, signature_base_str, hashlib.sha1).digest())

		"""
		Prepare Authorization header
		"""
		oauth['oauth_signature'] = oauth_signature
		auth_header = 'OAuth ' + ', '.join(['{}="{}"'.format(k,v) for k,v in oauth.iteritems()])

		"""
		Send request
		"""
		url = url + '?' + urllib.urlencode(query)
		request = urllib2.Request(url)
		request.add_header('Authorization', auth_header)
		request.add_header('X-Yahoo-App-Id', app_id)
		response = urllib2.urlopen(request).read()
		return response

	# 7/9/2019 rewritten to use JSON service which requires OAUTH - stupid yahoo
	def read_current_weather_conditions(self):
		response = self.get_weather_from_yahoo()

		jsonResponse = json.loads(response.decode('utf-8'))

		current_observation_date = datetime.fromtimestamp(jsonResponse['current_observation']['pubDate'])

		city = jsonResponse['location']['city']
		state = jsonResponse['location']['region']
		title = "Conditions for {0},{1} at {2}".format(city, state, current_observation_date)
				
		weather_code = int(jsonResponse['current_observation']['condition']['code'])
		
		temperature = jsonResponse['current_observation']['condition']['temperature']
		uom = 'F'
		conditions = jsonResponse['current_observation']['condition']['text']

		text = jsonResponse['forecasts'][0]['text']
		high = jsonResponse['forecasts'][0]['high']
		low = jsonResponse['forecasts'][0]['low']
		date = datetime.fromtimestamp(jsonResponse['forecasts'][0]['date'])
		day = jsonResponse['forecasts'][0]['day']
		forecast1 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['forecasts'][1]['text']
		high = jsonResponse['forecasts'][1]['high']
		low = jsonResponse['forecasts'][1]['low']
		date = datetime.fromtimestamp(jsonResponse['forecasts'][1]['date'])
		day = jsonResponse['forecasts'][1]['day']
		forecast2 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['forecasts'][2]['text']
		high = jsonResponse['forecasts'][2]['high']
		low = jsonResponse['forecasts'][2]['low']
		date = datetime.fromtimestamp(jsonResponse['forecasts'][2]['date'])
		day = jsonResponse['forecasts'][2]['day']
		forecast3 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['forecasts'][3]['text']
		high = jsonResponse['forecasts'][3]['high']
		low = jsonResponse['forecasts'][3]['low']
		date = datetime.fromtimestamp(jsonResponse['forecasts'][3]['date'])
		day = jsonResponse['forecasts'][3]['day']
		forecast4 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)

		text = jsonResponse['forecasts'][4]['text']
		high = jsonResponse['forecasts'][4]['high']
		low = jsonResponse['forecasts'][4]['low']
		date = datetime.fromtimestamp(jsonResponse['forecasts'][4]['date'])
		day = jsonResponse['forecasts'][4]['day']
		forecast5 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)
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
		
    
