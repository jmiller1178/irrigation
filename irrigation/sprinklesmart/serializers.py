from rest_framework import serializers
from . models import IrrigationSchedule, SystemMode, IrrigationSystem

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