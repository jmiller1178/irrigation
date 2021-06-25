#!/usr/bin/env bash

source /var/www/data/irrigation/envs/irrigation/bin/activate
cd /var/www/data/irrigation/irrigation
python manage.py record_current_weather_conditions
