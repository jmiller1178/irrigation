import json
from .models import Zone, IrrigationSystem, RpiGpio, WeatherCondition
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.contrib.sites.shortcuts import get_current_site
from rabbitmq.api import RabbitMqApi
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from .serializers import IrrigationSystemSerializer, WeatherConditionSerializer
from sprinklesmart.gpio.controller import turn_24_vac_on, turn_24_vac_off


import logging

logger = logging.getLogger(__name__)

RABBIT_MQ_API = RabbitMqApi(settings.RABBITMQ_HOST,
                            settings.RABBITMQ_USERNAME,
                            settings.RABBITMQ_PASSWORD)
EXCHANGE = settings.DEFAULT_AMQ_TOPIC


@receiver(post_save, sender=Zone)
def post_save_Zone(sender, instance, *args, **kwargs):
    zone = instance
    logger.info("Zone Save {0}".format(zone.json))
    zone.publish_zone_change()


@receiver(post_save, sender=IrrigationSystem)
def post_save_irrigation_system(sender, instance, *args, **kwargs):
    irrigation_system = instance
    # if the irrigation systemState is False we need
    # to ensure that we shutdown the entire system
    if irrigation_system.systemState:
        turn_24_vac_on()
    else:
        turn_24_vac_off()
    
    routing_key = "system"
    serializer = IrrigationSystemSerializer(instance, many=False)
    body = json.dumps(serializer.data)
    RABBIT_MQ_API.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)

"""
post_save_WeatherConditions
"""
@receiver(post_save, sender=WeatherCondition)
def post_save_weather_conditions(sender, instance, *args, **kwargs):
    weather_condition = instance
    routing_key = "weather"
    serializer = WeatherConditionSerializer(weather_condition, many=False)
    body = json.dumps(serializer.data)
    RABBIT_MQ_API.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)
