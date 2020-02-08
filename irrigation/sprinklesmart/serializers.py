from rest_framework import serializers
from .models import (IrrigationSchedule, Zone, SystemMode, IrrigationSystem,
    ConditionCode, WeatherCondition)

class IrrigationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationSchedule
        fields = ['zone', 'weekDays', 'duration', 'sortOrder',  ]

class SystemModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMode
        fields = '__all__'

class IrrigationSystemSerializer(serializers.ModelSerializer):
    system_mode = SystemModeSerializer(required=True)

    class Meta:
        model = IrrigationSystem
        fields = '__all__'

class ConditionCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionCode
        fields = '__all__'

"""
WeatherConditionSerializer is for serializing WeatherCondition
"""
class WeatherConditionSerializer(serializers.ModelSerializer):
    conditionCode = ConditionCodeSerializer(required=True)

    class Meta:
        model = WeatherCondition
        fields = ['title', 'conditionDateTime', 'conditionDateTime', 
        'temperature', 'unitOfMeasure', 'conditionCode', 'forecastDay1',
        'forecastDay2', 'forecastDay3', 'forecastDay4', 'forecastDay5',
        'raining_message',]

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['zoneId', 'shortName', 'displayName', 'enabled', 
        'visible', 'sortOrder', 'is_on', 'onDisplayText', 'offDisplayText',
        'locationName', 'currentState',]
