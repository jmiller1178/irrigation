from rest_framework import serializers
from .models import (IrrigationSchedule, Zone, SystemMode, IrrigationSystem,
    ConditionCode, WeatherCondition, Status, WeekDay, Schedule, RpiGpio, RpiGpioRequest)


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

class WeatherConditionSerializer(serializers.ModelSerializer):
    """
    WeatherConditionSerializer is for serializing WeatherCondition
    """
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

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class WeekDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDay
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class RpiGpioSerializer(serializers.ModelSerializer):
    zone = ZoneSerializer(required = True)

    class Meta:
        model = RpiGpio
        fields = '__all__'

class IrrigationScheduleSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(required=True)
    zone = ZoneSerializer(required=True)

    class Meta:
        model = IrrigationSchedule
        fields = ['zone', 'weekDays', 'duration', 'sortOrder',  ]

class RpiGpioRequestSerializer(serializers.ModelSerializer):
    rpiGpio = RpiGpioSerializer(required=True)
    status = StatusSerializer(required=True)

    class Meta:
        model = RpiGpioRequest
        fields = ['onDateTime', 'offDateTime', 'durationMultiplier',
                'on_date', 'on_time', 'off_date', 'off_time',
                'duration', 'remaining', 'rpiGpio', 'status', ]