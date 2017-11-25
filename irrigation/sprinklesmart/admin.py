# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Zone
from models import Schedule
from models import RpiGpio
from models import RpiGpioRequest
from models import IrrigationSchedule
from models import WeekDay
from models import Status
from models import IrrigationSystem
from models import ConditionCode, WeatherCondition

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'locationName', 'enabled', 'is_on',)
    ordering = ('zoneId',)
    fields = ('shortName', 'displayName', 'locationName', 'enabled', 'is_on', )
    readonly_fields = ('is_on',)

admin.site.register(Zone, ZoneAdmin)


class ScheduleAdmin(admin.ModelAdmin):
    fields = ('shortName', 'displayName','startTime', 'enabled',)
    list_display = ('displayName', 'shortName', 'startTime', 'enabled',)
    list_filter = ('enabled',)
    ordering = ('displayName',)

admin.site.register(Schedule, ScheduleAdmin)


class RpiGpioAdmin(admin.ModelAdmin):
    list_display = ('gpioName','gpioNumber','zone')
    fields = ('gpioName', 'gpioNumber','zone')
    
admin.site.register(RpiGpio, RpiGpioAdmin)


class RpiGpioRequestAdmin(admin.ModelAdmin):
  list_display = ('rpiGpio',  'onDateTime', 'offDateTime', 'status', 'durationMultiplier',)
  ordering = ('-id',)
  list_filter = ('status','onDateTime',)
  
admin.site.register(RpiGpioRequest, RpiGpioRequestAdmin)


class IrrigationScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'zone', 'duration','sortOrder',)
    ordering = ('schedule', 'sortOrder', 'zone',)
    list_filter = ('schedule',)
    filter_horizontal = ('weekDays',)
    
admin.site.register(IrrigationSchedule, IrrigationScheduleAdmin)


class StatusAdmin(admin.ModelAdmin):
    list_display = ('statusId', 'shortName','displayName',)
    ordering = ('statusId',)
    fields = ('statusId','shortName','displayName',)

admin.site.register(Status, StatusAdmin)

        
class ConditionCodeAdmin(admin.ModelAdmin):
	list_display = ('description', 'code')
	ordering = ('code',)

admin.site.register(ConditionCode, ConditionCodeAdmin)

class WeatherConditionAdmin(admin.ModelAdmin):
	list_display = ('conditionDateTime', 'temperature', 'conditionCode' )
	ordering = ('-conditionDateTime',)
	
admin.site.register(WeatherCondition, WeatherConditionAdmin)

admin.site.register(IrrigationSystem)

class WeekDayAdmin(admin.ModelAdmin):
    list_display = ('longName', 'shortName', 'weekDay',)
    ordering = ('weekDay',)
    
admin.site.register(WeekDay, WeekDayAdmin)
