import json
from .models import Zone, IrrigationSystem
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.contrib.sites.shortcuts import get_current_site
from rabbitmq.api import RabbitMqApi
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from .serializers import IrrigationSystemSerializer

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Zone)
def post_save_Zone(sender, instance, *args, **kwargs):
    zone = instance
    logger.info("Zone Save {0}".format(zone.json))
    zone.publish_zone_change()


@receiver(post_save, sender=IrrigationSystem)
def post_save_IrrigationSystem(sender, instance, *args, **kwargs):
    
    rabbit_mq_api = RabbitMqApi(settings.RABBITMQ_HOST,
                                settings.RABBITMQ_USERNAME,
                                settings.RABBITMQ_PASSWORD)
    exchange = settings.DEFAULT_AMQ_TOPIC
    routing_key = "system"
    serializer = IrrigationSystemSerializer(instance, many=False)
    body = json.dumps(serializer.data)
    rabbit_mq_api.publish(exchange=exchange,
                          routing_key=routing_key,
                          body=body)