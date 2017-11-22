# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib import admin
from datetime import datetime, date, timedelta
import pytz

class Zone(models.Model):
    class Meta:
        db_table = 'zone'
        verbose_name = 'Zone'
        verbose_name_plural = "Zones"
    zoneId = models.IntegerField(primary_key="True")
    shortName = models.CharField(max_length=45)
    shortName.verbose_name= "Short Name"
    displayName = models.CharField(max_length=255)
    displayName.verbose_name = "Display Name"
    enabled = models.BooleanField(default = True)
      
    is_on = models.BooleanField(default = False)
    is_on.verbose_name = "Current State"

    locationName = models.CharField(max_length=45)
    locationName.verbose_name = "Location"
    def currentState(self):
      if self.is_on:
        return "ON"
      else:
        return "OFF"
    def __unicode__(self):
      return self.displayName


# 6/5/2013 JRM - added this class
class IrrigationSystem(models.Model):
    class Meta:
        db_table = "irrigation_system"
        verbose_name = "Irrigation System"
        verbose_name_plural = "Irrigation System"

    #id = models.IntegerField(primary_key="True", db_column="id")
    systemState = models.IntegerField(db_column="system_state")

    def __unicode__(self):
        if self.systemState == 1:
            return "Enabled"
        else:
            return "Disabled"

class Status(models.Model):
    class Meta:
        db_table = "status"
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
    statusId = models.IntegerField(primary_key="True")
    statusId.verbose_name = "Status ID"
    shortName = models.CharField(max_length=45)
    shortName.verbose_name = "Abbreviation"
    displayName = models.CharField(max_length=128)
    displayName.verbose_name = "Status"
    def __unicode__(self):
        return self.displayName

        
class WeekDay(models.Model):
    class Meta:
        db_table="weekday"
        verbose_name="Week Day"
        verbose_name_plural = "Week Days"
    weekDayId = models.IntegerField(primary_key="True")
    shortName = models.CharField(max_length=10)
    longName = models.CharField(max_length=50)
    def __unicode__(self):
        return self.shortName
    
class Schedule(models.Model):
    class Meta:
        db_table="schedule"
        verbose_name= "Schedule"
        verbose_name_plural = "Schedules"
    scheduleId = models.IntegerField(primary_key="True")
    scheduleId.verbose_name = "Schedule Id"
    shortName = models.CharField(max_length=45)
    shortName.verbose_name= "Short Name"
    displayName = models.CharField(max_length=255)
    displayName.verbose_name = "Display Name"
    enabled = models.BooleanField(default=True)
    startTime = models.TimeField()
    startTime.verbose_name = "Start Time"

    def __unicode__(self):
        return self.displayName


class RpiGpio(models.Model):
    class Meta:
        db_table="rpiGpio"
        verbose_name="RPI GPIO"
        verbose_name_plural = "RPI GPIO"
    rpiGpioId = models.IntegerField(primary_key="True")
    rpiGpioId.verbose_name = "RPI GPIO Id"
    zone = models.ForeignKey(Zone, db_column="zoneId")
    gpioName = models.CharField(max_length=45)
    gpioName.verbose_name = "GPIO Name"
    gpioNumber = models.CharField(max_length=45)
    gpioNumber.verbose_name= "GPIO Number"

    def displayName(self):
        return self.zone.displayName + ' ' + self.gpioName
    def __unicode__(self):
        return self.gpioName


class RpiGpioRequest(models.Model):
    class Meta:
        db_table = "rpiGpioRequest"
        verbose_name = "RPI GPIO Request"
        verbose_name_plural = "RPI GPIO Requests"
    rpiGpio = models.ForeignKey(RpiGpio,  db_column="rpiGpioId")
    rpiGpio.verbose_name = "RPI GPIO"
    
    onDateTime = models.DateTimeField()
    onDateTime.verbose_name = "On Date & Time"
    offDateTime = models.DateTimeField()
    offDateTime.verbose_name = "Off Date & Time"

    status = models.ForeignKey(Status,  db_column="statusId")

    def onDate(self):
        return self.onDateTime.strftime("%Y-%m-%d")

    def onTime(self):
        return self.onDateTime.strftime("%I:%M %p")

    def offDate(self):
        return self.offDateTime.strftime("%Y-%m-%d")

    def offTime(self):
        return self.offDateTime.strftime("%I:%M %p")

    def duration(self):
        duration = (self.offDateTime - self.onDateTime).seconds / 60
        return duration

    def remaining(self):
		
        if datetime.now(pytz.utc) > self.offDateTime:
            remaining = 0
        elif datetime.now(pytz.utc) > self.onDateTime:
          remaining = ((self.offDateTime - datetime.now(pytz.utc)).seconds / 60) + 1
        else:
          remaining =(self.offDateTime - self.onDateTime).seconds / 60
        return remaining

    def __unicode__(self):
        return self.rpiGpio.displayName() + ' ' + self.status.displayName + ' ON: ' + str(self.onDateTime) + ' OFF: ' + str(self.offDateTime)

  
class IrrigationSchedule(models.Model):
    class Meta:
        db_table = "irrigationSchedule"
        verbose_name = "Irrigation Schedule"
        verbose_name_plural = "Irrigation Schedules"
    schedule = models.ForeignKey(Schedule,  db_column="scheduleId")
    zone = models.ForeignKey(Zone,  db_column="zoneId")
    weekDays = models.ManyToManyField(WeekDay)
    weekDays.verbose_name = "Week Days"
    weekDays.verbose_name_plural = "Week Days"
    duration = models.IntegerField()
    duration.verbose_name = "Duration"    

    def displayName(self):
      return self.schedule.displayName + ' ' + self.zone.displayName
    def __unicode__(self):
      return self.displayName()


class ConditionCode(models.Model):
    class Meta:
        db_table = "conditionCode"
        verbose_name = "Condition Code"
        verbose_name_plural = "Condition Codes"
    code = models.IntegerField(primary_key="True")
    code.verbose_name = "Condition Code"
    description = models.CharField(max_length=50)
    description.verbose_name = "Condition"

    def IsRaining(self):
      return self.code in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 35, 37, 38, 39, 40, 45, 47)

    def __unicode__(self):
        return self.description
        

class WeatherCondition(models.Model):
    class Meta:
        db_table = "weatherCondition"
        verbose_name = "Weather Condition"
        verbose_name_plural = "Weather Conditions"
   
    conditionDateTime = models.DateTimeField()
    conditionDateTime.verbose_name = "Date & Time"
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    conditionCode = models.ForeignKey(ConditionCode, db_column="code")



