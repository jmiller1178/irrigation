#!/usr/bin/env bash

source /var/www/data/irrigation/envs/irrigation/bin/activate
cd /var/www/data/irrigation/irrigation
python manage.py initialize_rpigpio

