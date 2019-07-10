"""
Weather API Python sample code

Copyright 2019 Oath Inc. Licensed under the terms of the zLib license see https://opensource.org/licenses/Zlib for terms.

$ python --version
Python 2.7.10

"""
import time, uuid, urllib, urllib2
import hmac, hashlib
from base64 import b64encode
import json
from datetime import datetime, date, timedelta
from dateutil import parser
"""
Basic info
"""
url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss'
method = 'GET'
app_id = 'RM92pQ50'
consumer_key = 'dj0yJmk9YWxGUmNERE8yY3ZPJmQ9WVdrOVVrMDVNbkJSTlRBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWZk'
consumer_secret = '10f18a7036102224a29c5a8c9404920ae5594311'
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
jsonResponse = json.loads(response.decode('utf-8'))

current_observation_date = datetime.fromtimestamp(jsonResponse['current_observation']['pubDate'])

city = jsonResponse['location']['city']
state = jsonResponse['location']['region']
title = "Conditions for {0},{1} at {2}".format(city, state, current_observation_date)
weather_code = int(jsonResponse['current_observation']['condition']['code'])
temperature = jsonResponse['current_observation']['condition']['temperature']
text = jsonResponse['forecasts'][0]['text']
print(title)
print(weather_code)
print(temperature)
text = jsonResponse['forecasts'][0]['text']
high = jsonResponse['forecasts'][0]['high']
low = jsonResponse['forecasts'][0]['low']
date = datetime.fromtimestamp(jsonResponse['forecasts'][0]['date'])
day = jsonResponse['forecasts'][0]['day']
uom = 'F'
forecast1 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, uom, low, uom)
print (forecast1)


