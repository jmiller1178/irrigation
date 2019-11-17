from rest_framework import serializers
from models import IrrigationSchedule

class IrrigationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationSchedule
        fields = ['zone', 'weekDays', 'duration', 'sortOrder',  ]
    
        
