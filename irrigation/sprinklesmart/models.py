# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from datetime import datetime
from django.db import models
from django.conf import settings
from django.db.models import Q
from rabbitmq.api import RabbitMqApi

class Zone(models.Model):
    """
    Zone - represents an OUTPUT which could be to a sprinkler
    or could be the system enable or valve enable
    """
    zoneId = models.IntegerField(primary_key="True")
    shortName = models.CharField(max_length=45)
    shortName.verbose_name = "Short Name"
    displayName = models.CharField(max_length=255)
    displayName.verbose_name = "Display Name"
    enabled = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    sortOrder = models.IntegerField(default=0, blank=False)  
    is_on = models.BooleanField(default=False)
    is_on.verbose_name = "Current State"
    onDisplayText = models.CharField(default="On", max_length=255, null=False,
        blank=True, verbose_name="Text to display when ON")
    offDisplayText = models.CharField(default="Off", max_length=255, null=False, 
        blank=True, verbose_name="Text to display when OFF")
    locationName = models.CharField(max_length=45)
    locationName.verbose_name = "Location"

    class Meta:
        db_table = 'zone'
        verbose_name = 'Zone'
        verbose_name_plural = "Zones"
        ordering = ['sortOrder']

    def __unicode__(self):
        return self.displayName

    def __str__(self):
        return self.displayName

    @property
    def currentState(self):
        if self.is_on:
            return self.onDisplayText
        else:
            return self.offDisplayText

    
class SystemMode(models.Model):
    """
    SystemMode is used for keeping track of Automatic or Manual system mode
    """
    name = models.CharField(max_length=255, null=False, blank=False)
    short_name  = models.CharField(max_length=1, null=False, blank=False)

    class Meta:
        db_table = "system_mode"
        verbose_name = "System Mode"
        verbose_name_plural = "System Modes"

    @property
    def automatic_mode(self):
        """
        true when the system is in automatic mode
        """
        return self.short_name == 'A'

    @property
    def manual_mode(self):
        """
        true when the system is in manual mode
        """
        return self.short_name == 'M'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class IrrigationSystem(models.Model):
    """
    IrrigationSystem is used for keeping track of the state of the system (Enabled/Disabled)
    plus the state of the valves (Enabled/Disabled)
    and the system state (Automatic/Manual)
    """
    systemState = models.BooleanField(db_column="system_state")
    system_mode = models.ForeignKey(SystemMode, blank=False, null=False, on_delete=models.PROTECT)
    system_enabled_zone = models.ForeignKey(Zone, blank=False, null=False, related_name="system_enabled_zone", on_delete=models.PROTECT)
    valves_enabled_zone = models.ForeignKey(Zone, blank=False, null=False, related_name="valves_enabled_zone", on_delete=models.PROTECT)

    class Meta:
        db_table = "irrigation_system"
        verbose_name = "Irrigation System"
        verbose_name_plural = "Irrigation System"

    def __str__(self):
        state = None
        if self.systemState == True:
            state = "Enabled"
        else:
            state = "Disabled"
        return state

    def toggle_system_mode(self):
        """
        toggle system mode from / to automatic / manual
        """
        # current mode is Automatic
        if self.system_mode.automatic_mode:
            # going from automatic to manual
            system_mode = SystemMode.objects.get(short_name='M')
            # need to cancel all open requests here
            rpi_gpio_on_requests = RpiGpioRequest.objects.filter(Q(status=1) | Q(status=4))
            cancelled_status = Status.objects.get(pk=3)
            # cancel the ON requests
            for rpi_gpio_on_reqest in rpi_gpio_on_requests:
                rpi_gpio_on_reqest.status = cancelled_status
                rpi_gpio_on_reqest.save()
        
        # current mode is Manual
        if self.system_mode.manual_mode:
            # going from manual to automatic
            system_mode = SystemMode.objects.get(short_name='A')

        self.system_mode = system_mode
        self.save()
        return self

class Status(models.Model):
    """
    Status is used to represent various states that the RPi GPIO requests go through
    """
    statusId = models.IntegerField(primary_key="True")
    statusId.verbose_name = "Status ID"
    shortName = models.CharField(max_length=45)
    shortName.verbose_name = "Abbreviation"
    displayName = models.CharField(max_length=128)
    displayName.verbose_name = "Status"

    class Meta:
        db_table = "status"
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.displayName

class WeekDay(models.Model):
    """
    WeekDay is a day of the week
    """
    weekDayId = models.IntegerField(primary_key="True")
    shortName = models.CharField(max_length=10)
    longName = models.CharField(max_length=50)
    weekDay = models.IntegerField(default=0)

    class Meta:
        db_table = "weekday"
        verbose_name = "Week Day"
        verbose_name_plural = "Week Days"

    def __str__(self):
        return self.shortName
            
class Schedule(models.Model):
    """ 
    Schedule represents a schedule
    """
    scheduleId = models.IntegerField(primary_key="True")
    scheduleId.verbose_name = "Schedule Id"
    shortName = models.CharField(max_length=45)
    shortName.verbose_name= "Short Name"
    displayName = models.CharField(max_length=255)
    displayName.verbose_name = "Display Name"
    enabled = models.BooleanField(default=True)
    startTime = models.TimeField()
    startTime.verbose_name = "Start Time"

    class Meta:
        db_table = "schedule"
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        return self.displayName

class RpiGpio(models.Model):
    """
    RpiGpio is a IO point on the RaspberryPI
    """
    rpiGpioId = models.IntegerField(primary_key="True")
    rpiGpioId.verbose_name = "RPI GPIO Id"
    zone = models.ForeignKey(Zone, db_column="zoneId", on_delete=models.PROTECT)
    gpioName = models.CharField(max_length=45)
    gpioName.verbose_name = "GPIO Name"
    gpioNumber = models.CharField(max_length=45)
    gpioNumber.verbose_name = "GPIO Number"

    class Meta:
        db_table = "rpiGpio"
        verbose_name = "RPI GPIO"
        verbose_name_plural = "RPI GPIO"

    def __str__(self):
        return self.gpioName

    @property
    def displayName(self):
        """ 
        display name for this rpi GPIO
        """
        return self.zone.displayName + ' ' + self.gpioName

class RpiGpioRequest(models.Model):
    """
    RpiGpioRequest records are created to schedule a zone (RpiGpio) to turn on and then off
    """
    rpiGpio = models.ForeignKey(RpiGpio, db_column="rpiGpioId", on_delete=models.PROTECT)
    rpiGpio.verbose_name = "RPI GPIO"
    
    onDateTime = models.DateTimeField()
    onDateTime.verbose_name = "On Date & Time"
    offDateTime = models.DateTimeField()
    offDateTime.verbose_name = "Off Date & Time"

    status = models.ForeignKey(Status, db_column="statusId", on_delete=models.PROTECT)
    durationMultiplier = models.FloatField(default=1.0)

    class Meta:
        db_table = "rpiGpioRequest"
        verbose_name = "RPI GPIO Request"
        verbose_name_plural = "RPI GPIO Requests"
    
    @property
    def on_date(self):
        """
        on date
        """
        return self.onDateTime.strftime("%Y-%m-%d")

    @property
    def on_time(self):
        """
        on time
        """
        return self.onDateTime.strftime("%I:%M %p")
    
    @property
    def off_date(self):
        """
        off date
        """
        return self.offDateTime.strftime("%Y-%m-%d")

    @property
    def off_time(self):
        """
        off time
        """
        return self.offDateTime.strftime("%I:%M %p")

    @property
    def duration(self):
        """
        on duration
        """
        duration = (self.offDateTime - self.onDateTime).seconds / 60
        return duration

    @property
    def remaining(self):
        """
        remaining time for this scheduled request
        """
        if datetime.now() > self.offDateTime:
            remaining = 0
        elif datetime.now() > self.onDateTime:
          remaining = ((self.offDateTime - datetime.now()).seconds / 60) + 1
        else:
          remaining =(self.offDateTime - self.onDateTime).seconds / 60
        return remaining

    def __str__(self):
        return self.rpiGpio.displayName() + ' ' + self.status.displayName + ' ON: ' + str(self.onDateTime) + ' OFF: ' + str(self.offDateTime)
  
class IrrigationSchedule(models.Model):
    """
    IrrigationSchedule is part of the setup to build the schedule 
    """
    schedule = models.ForeignKey(Schedule,  db_column="scheduleId", on_delete=models.PROTECT)
    zone = models.ForeignKey(Zone,  db_column="zoneId", on_delete=models.PROTECT)
    weekDays = models.ManyToManyField(WeekDay)
    weekDays.verbose_name = "Week Days"
    weekDays.verbose_name_plural = "Week Days"
    duration = models.IntegerField()
    duration.verbose_name = "Duration"    
    sortOrder = models.IntegerField(default=0)

    class Meta:
        db_table = "irrigationSchedule"
        verbose_name = "Irrigation Schedule"
        verbose_name_plural = "Irrigation Schedules"
        ordering = ['sortOrder']

    @property
    def displayName(self):
        """
        display name
        """
        return self.schedule.displayName + ' ' + self.zone.displayName

    def __str__(self):
      return self.displayName()

class ConditionCode(models.Model):
    """
    Weather condition codes
    """
    code = models.IntegerField(primary_key="True")
    code.verbose_name = "Condition Code"
    description = models.CharField(max_length=50)
    description.verbose_name = "Condition"

    @property
    def IsRaining(self):
        """
        codes for raining - returns true if match
        """
        return self.code in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 
        12, 13, 17, 18, 35, 37, 38, 39, 40, 45, 47)

    class Meta:
        db_table = "conditionCode"
        verbose_name = "Condition Code"
        verbose_name_plural = "Condition Codes"

    def __str__(self):
        return self.description    

class WeatherCondition(models.Model):
    """
    current weather condition
    """
    title = models.CharField(max_length=512, default='')
    conditionDateTime = models.DateTimeField()
    conditionDateTime.verbose_name = "Date & Time"
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    unitOfMeasure = models.CharField(max_length=10, default="F")
    conditionCode = models.ForeignKey(ConditionCode, db_column="code", on_delete=models.PROTECT)
    forecastDay1 = models.CharField(max_length=512, default='')
    forecastDay2 = models.CharField(max_length=512, default='')
    forecastDay3 = models.CharField(max_length=512, default='')
    forecastDay4 = models.CharField(max_length=512, default='')
    forecastDay5 = models.CharField(max_length=512, default='')

    class Meta:
        db_table = "weatherCondition"
        verbose_name = "Weather Condition"
        verbose_name_plural = "Weather Conditions"
        
    def __str__(self):
        return self.title

    @property
    def raining_message(self):
        message = ""
        if self.conditionCode.IsRaining:
            message = "It is raining outside"
        else:
            message = "It is not raining outside"
        return message



