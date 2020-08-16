import json
from .models import (Zone, IrrigationSystem, RpiGpio, WeatherCondition,
    RpiGpioRequest, Schedule)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from rabbitmq.api import RabbitMqApi
from .serializers import (IrrigationSystemSerializer, WeatherConditionSerializer, 
    ZoneSerializer, RpiGpioRequestSerializer)
from sprinklesmart.gpio.controller import turn_24_vac_on, turn_24_vac_off

import logging

logger = logging.getLogger(__name__)

EXCHANGE = settings.DEFAULT_AMQ_TOPIC

@receiver(post_save, sender=Zone)
def post_save_zone(sender, instance, *args, **kwargs):
    """
    invoked after Zone.save()
    """
    zone = instance
    routing_key = "zone"
    serializer = ZoneSerializer(zone, many=False)
    body = json.dumps(serializer.data)
    rabbit_mq_api = RabbitMqApi(settings.RABBITMQ_HOST,
                            settings.RABBITMQ_USERNAME,
                            settings.RABBITMQ_PASSWORD)


    rabbit_mq_api.publish(exchange=EXCHANGE,
                        routing_key=routing_key,
                        body=body)

@receiver(post_save, sender=IrrigationSystem)
def post_save_irrigation_system(sender, instance, *args, **kwargs):
    """
    invoked after IrrigationSystem.save
    """
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
    rabbit_mq_api = RabbitMqApi(settings.RABBITMQ_HOST,
                            settings.RABBITMQ_USERNAME,
                            settings.RABBITMQ_PASSWORD)

    rabbit_mq_api.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)
    # trigger a schedule irrigation controller invocation
    irrigation_system.schedule_irrigation_controller()        


@receiver(post_save, sender=WeatherCondition)
def post_save_weather_conditions(sender, instance, *args, **kwargs):
    """
    post_save_WeatherConditions
    """
    weather_condition = instance
    routing_key = "weather"
    serializer = WeatherConditionSerializer(weather_condition, many=False)
    body = json.dumps(serializer.data)
    rabbit_mq_api = RabbitMqApi(settings.RABBITMQ_HOST,
                            settings.RABBITMQ_USERNAME,
                            settings.RABBITMQ_PASSWORD)


    rabbit_mq_api.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)

@receiver(post_save, sender=RpiGpioRequest)
def post_save_rpi_gpio_request(sender, instance, *args, **kwargs):
    """
    post save RpiGpioRequest
    """
    rpi_gpio_request = instance
    routing_key = "rpigpiorequest"
    serializer = RpiGpioRequestSerializer(rpi_gpio_request, many=False)
    body = json.dumps(serializer.data)
    rabbit_mq_api = RabbitMqApi(settings.RABBITMQ_HOST,
                            settings.RABBITMQ_USERNAME,
                            settings.RABBITMQ_PASSWORD)

    rabbit_mq_api.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)

    # see if there are anymore pending requests
    # if there are none then we publish a message telling the ui to remove
    # all of the RPi GPIO requests - basically, clear the table
    pending_or_active_requests = RpiGpioRequest.pending_or_active_requests.all()
    if pending_or_active_requests.count() == 0:
        routing_key = "norpigpiorequests"
        body = "norpigpiorequests"
        rabbit_mq_api.publish(exchange=EXCHANGE,
                          routing_key=routing_key,
                          body=body)


@receiver(post_save, sender=Schedule)
def post_save_schedule(sender, instance, *args, **kwargs):
    """
    post save Schedule
    """
    # force an update of the schedule upon saving 
    irrigation_system = IrrigationSystem.objects.get(pk=1)
    irrigation_system.schedule_irrigation_controller()        

