from .models import Zone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.contrib.sites.shortcuts import get_current_site

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Zone)
def post_save_Zone(sender, instance, *args, **kwargs):
    zone = instance
    logger.info("Zone Save {0}".format(zone.json))
    zone.publish_zone_change()


