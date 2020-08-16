# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, date
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from sprinklesmart.api.weather import WeatherAPI

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
            rpi_gpio_on_requests = RpiGpioRequest.pending_or_active_requests.all()
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

    def schedule_irrigation_controller(self):
                # are we in automatic mode and the system enabled
        if self.system_mode.automatic_mode and\
            self.systemState:

            # active_status = get_object_or_404(Status, pk=4) # 4 is active
            pending_status = get_object_or_404(Status, pk=1) # 1 is pending

            # Let's start by checking if ANYTHING is scheduled for today because, if there is, then we shouldn't
            # have to execute any of the code below, right??
            requests = RpiGpioRequest.pending_requests.all()
        
            if requests.count() == 0:
                weather_api = WeatherAPI()
                # there is nothing scheduled for today so do the scheduling process
            
                # look for active schedule(s) with a start time within the next hour
                enabled_schedules = Schedule.objects.filter(enabled=True)
                sprinkle_smart_multiplier = weather_api.get_sprinkle_smart_multiplier()
            
                # retrieve IrrigationSchedule records for this day of the week and for the above Schedule
                current_time = datetime.now()

                # find the WeekDay object for today
                week_day = get_object_or_404(WeekDay, weekDay=current_time.weekday())
            
                for schedule in enabled_schedules:
                
                    schedule_time = datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute)
                    if schedule_time > current_time:
                        delta_time = schedule_time-current_time
                        minutes_in_future = int(delta_time.seconds / 60)
                    
                        if minutes_in_future < 480:
                            # we're less than 8 hours away from scheduled start time so need to stup the RpiGpioRequests per that schedule
                            irrigation_schedules = schedule.irrigationschedule_set.filter(weekDays=week_day).order_by('sortOrder')
                            zone_start_time = datetime(current_time.year, current_time.month, current_time.day, schedule.startTime.hour, schedule.startTime.minute)

                            for irrigation_schedule in irrigation_schedules:
                                # create RpiGpioRequest records for today
                                # there should only be one rpiGpio per zone but it is a set so iterate anyway
                                rpigpios = irrigation_schedule.zone.rpigpio_set.all()
                            
                                for rpigpio in rpigpios:            
                                    # check for an existing RpiGpioRequest to avoid
                                    # double scheduling
                                    
                                    rpi_gpio_request = RpiGpioRequest.todays_requests.filter(rpiGpio=rpigpio)
                                    if rpi_gpio_request.count() == 0:
                                        scheduled_request = RpiGpioRequest()
                                        scheduled_request.rpiGpio = rpigpio
                                        scheduled_request.onDateTime = zone_start_time
                                    
                                        duration_minutes = int(irrigation_schedule.duration * sprinkle_smart_multiplier)
                                        zone_end_time = zone_start_time + timedelta(minutes=duration_minutes)
                                    
                                        scheduled_request.offDateTime = zone_end_time
                                        scheduled_request.status = pending_status
                                        scheduled_request.durationMultiplier = sprinkle_smart_multiplier
                                        scheduled_request.save()
                                        zone_start_time = zone_end_time

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
    shortName.verbose_name = "Short Name"
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

class TodaysRpiGpioRequestManager(models.Manager):
    def get_queryset(self):
        todays_requests = super().get_queryset().filter(
            onDateTime__contains=date.today(),
            status__statusId__in=(1,4)).order_by('onDateTime')
        
        # active_todays_requests = todays_requests.filter(status__statusId=4)
        # pending_todays_requests = todays_requests.filter(status__statusId=1)
        # complete_todays_requests = todays_requests.filter(status__statusId=2)
        # cancelled_todays_requests = todays_requests.filter(status__statusId=3)

        # if there are no active or pending requests
        # there is no point in returning anything to display
        #if active_todays_requests.count() == 0 and\
        #   pending_todays_requests.count() == 0:
        #    todays_requests = None

        return todays_requests

class OffRequestsManager(models.Manager):
    def get_queryset(self):
        current_time = datetime.now()
        active_status = get_object_or_404(Status, pk=4) # 4 is active
        return super().get_queryset().filter(status=active_status, offDateTime__year=current_time.year,
            offDateTime__month=current_time.month, offDateTime__day=current_time.day,
            offDateTime__hour=current_time.hour, offDateTime__minute=current_time.minute)

class PendingRequestsManager(models.Manager):
    def get_queryset(self):
        current_time = datetime.now()
        
        pending_status = get_object_or_404(Status, pk=1) # 1 is pending
        return super().get_queryset().filter(status=pending_status, onDateTime__year=current_time.year,
            onDateTime__month=current_time.month, onDateTime__day=current_time.day,
            onDateTime__hour=current_time.hour, onDateTime__minute=current_time.minute)
            

class PendingOrActiveRequestsManager(models.Manager):
    def get_queryset(self):
        pending_status = get_object_or_404(Status, pk=1) # 1 is pending
        active_status = get_object_or_404(Status, pk=4) # 4 is active

        return super().get_queryset().filter(Q(status=pending_status) | Q(status=active_status), onDateTime__contains=date.today())

class ActiveRequestsManager(models.Manager):
    def get_queryset(self):
        active_status = get_object_or_404(Status, pk=4) # 4 is active
        return super().get_queryset().filter(status=active_status,
            onDateTime__contains=date.today())

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

    todays_requests = TodaysRpiGpioRequestManager()
    off_requests = OffRequestsManager()
    pending_requests = PendingRequestsManager()
    active_requests = ActiveRequestsManager()
    pending_or_active_requests = PendingOrActiveRequestsManager()

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

        duration = self.offDateTime - self.onDateTime
        duration_in_s = duration.total_seconds()
        duration = divmod(duration_in_s, 60)[0]
        return duration

    @property
    def remaining(self):
        """
        remaining time for this scheduled request
        """
        current_time = datetime.now()

        remaining = 0

        if self.offDateTime > current_time:
            remaining = self.offDateTime - current_time
            remaining_in_s = remaining.total_seconds()    
            remaining = divmod(remaining_in_s, 60)[0] 
            

        if remaining > self.duration:
            remaining = self.duration

        return remaining

    @property
    def zone(self):
        return self.rpiGpio.zone

    def __str__(self):
        return self.rpiGpio.displayName + ' ' + self.status.displayName + ' ON: ' + str(self.onDateTime) + ' OFF: ' + str(self.offDateTime)
  
class IrrigationSchedule(models.Model):
    """
        IrrigationSchedule is part of the setup to build the schedule
    """
    schedule = models.ForeignKey(Schedule, db_column="scheduleId", on_delete=models.PROTECT)
    zone = models.ForeignKey(Zone, db_column="zoneId", on_delete=models.PROTECT)
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
      return self.displayName

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



