# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

class SprinklesmartConfig(AppConfig):
    name = 'sprinklesmart'
    verbose_name = "Sprinklesmart"

    def ready(self):
        import sprinklesmart.signals

