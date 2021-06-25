#!/usr/bin/python
# -*- coding: utf-8 -*-
# 2/6/2013 JRM - combined scheduleDbDaemon & rpiGpioDaemon to make timing more consistent
#                         and reduce CPU load
# 2/13/2013 JRM - changed to reflect new database schema
# 3/2/2013 JRM - removed zoneRpiGpio table because it was worthless
# 3/7/2013 JRM - added weather conditions data collection
# 3/9/2013 JRM - changed rpiGpioRequest table schema to include onDateTime & offDateTime 
# 4/18/2013 JRM - added logic to check for rain and take appropriate action and refined scheduling logic
# 5/11/2013 JRM - added SprinkleSmart multiplier
# 6/5/2013 JRM - added System Enable / Diable to admin
# 7/1/2013 JRM - added check for access to internet before trying to call weather webservice
# 7/7/2016 JRM - changed to use yahoo weather API yql since they stopped supporting the pywapi call
#
import sqlite3 as lite
import daemon
import time
import sys
from datetime import datetime, date, timedelta
import logging
import uuid
import RPi.GPIO as GPIO
import urllib2
import urllib
import json
from urllib import urlencode

def OutputCommand(ioid, zoneId, command, con):
    # this function actually controls the RPi GPIO outputs
    # and it updates the zone table to indicate when a particular zone goes on or off
    # we can use the zone table to tell which outputs are off
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(ioid, GPIO.OUT)

    if command == "ON":
        GPIO.output(ioid, GPIO.HIGH)
        updSql = "UPDATE zone SET is_on=1 WHERE zoneId=?;"
        updCur = con.cursor()
        updCur.execute(updSql,(zoneId, ))
        con.commit()

    if command == "OFF":
        GPIO.output(ioid, GPIO.LOW)
        updSql = "UPDATE zone SET is_on=0 WHERE zoneId=?;"
        updCur = con.cursor()
        updCur.execute(updSql,(zoneId, ))
        con.commit()
  
def TurnAllOutputsOff(con):
    # this function iterates through all defined rpiGpio records
    # and invokes the OutputCommand to turn them all off
    sql = "SELECT \
      rpiGpio.gpioNumber, \
      rpiGpio.zoneId \
       FROM rpiGpio;"
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)

    rows = cur.fetchall()
    # need to fulfill the request
    for row in rows:
        ioid = row["gpioNumber"]
        zoneId = row["zoneId"]
        OutputCommand(ioid=ioid, zoneId=str(zoneId), command="OFF",con=con)
    
def CheckIrrigationSchedule(con):
    today = date.today()
    # 3/9/2013 JRM - let's start by checking if ANYTHING is scheduled for today because, if there is, then we shouldn't
    # have to execute any of the code below, right??
    # 5/11/2013 JRM - added the check for statusId IN (1,4) to the sql
    sql = "SELECT \
            COUNT(id) AS row_count \
           FROM \
            rpiGpioRequest \
           WHERE \
            onDateTime >= ? \
           AND statusId IN (1,4)"
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql,(today,))
    row = cur.fetchone()

    # check if there is anything scheduled for today
    if row["row_count"] == 0:
        # there is nothing scheduled for today so do the schedule
        # 3/2/2013 - changed to return all records for the day - everything will be scheduled in advance this way
        # 7/5/2013 - changed to return only the records scheduled for the next hour - we're examining the schedule.startTime hour
        # and checking to see if it is 1+ the value of the current hour so, if the schedule start time is for 4 am and we're in the 3 am hour
        # records will be returned.  This helps accomodate multiple schedules within a day
        sql = "SELECT \
            schedule.displayName AS scheduleDisplayName,\
            schedule.startTime AS scheduleStartTime, \
            zone.displayName AS zoneDisplayName,\
            irrigationSchedule.zoneId, \
            irrigationSchedule.duration, \
            rpiGpio.rpiGpioId, \
            rpiGpio.gpioName,\
            rpiGpio.gpioNumber \
            FROM \
            irrigationSchedule \
            JOIN irrigationSchedule_weekDays ON irrigationSchedule.id=irrigationSchedule_weekDays.irrigationschedule_id \
            JOIN rpiGpio ON irrigationSchedule.zoneId=rpiGpio.zoneId \
            JOIN schedule ON irrigationSchedule.scheduleId=schedule.scheduleId \
            JOIN zone ON irrigationSchedule.zoneId=zone.zoneId \
            WHERE \
            irrigationSchedule_weekDays.weekday_id=(strftime('%w','now','localtime')+1) \
            AND CAST(strftime('%H','now','localtime') AS integer)+1=CAST(strftime('%H',schedule.startTime) AS integer) \
            AND zone.enabled=1 \
            AND schedule.enabled=1 \
            ORDER BY zone.zoneId ASC;"

        
        con.row_factory = lite.Row
        cur = con.cursor() 
        cur.execute(sql)
        
        # 5/11/2013 JRM - SprinkleSmart Multipler
        multiplier = GetSprinkleSmartMultiplier(con)

        # get the schedule start time from the 1st row - this will end up being the 1st initial start time for the 1st zone
        row = cur.fetchone()
        # 5/11/2013 JRM - added check for None since there may not be anything scheduled for today
        if row is not None:
            onDateTime=datetime.strptime(str(today) + ' ' + str(row["scheduleStartTime"]), '%Y-%m-%d %H:%M:%S')

        cur.execute(sql)
        rows = cur.fetchall()
        # do the INSERT INTO the rpiGpioRequest table
        for row in rows:
            rpiGpioId=row["rpiGpioId"]
            
            duration = int(row["duration"] * multiplier)

            # calculate the OFF timestamp by adding the duration to the ON timestamp
            offDateTime = onDateTime + timedelta(minutes=duration)
            

            # 4/18/2013 JRM - since we cannot travel back in time if the calculated onDateTime is <= now
            # we skip this zone by not executing the INSERT statement
            if onDateTime > datetime.now():
                # this is the INSERT statement to create a request record in the rpiGpioRequest table
                insertSql = "INSERT INTO rpiGpioRequest(rpiGpioId, onDateTime, offDateTime, statusId)\
                              VALUES(?,?,?,?)"
                
                insertCur = con.cursor()
                insertCur.execute(insertSql,(rpiGpioId, onDateTime, offDateTime, 1))

            # the next zone's ON timestamp is the previous zone's OFF timestamp
            onDateTime = offDateTime
        
        # save it to the database    
        con.commit()            

# 5/11/2013 JRM SprinkleSmart Multiplier Logic is here
def GetSprinkleSmartMultiplier(con):
    multiplier = 1.0
    sql = "SELECT COUNT(*) AS total_row_count FROM \
            weatherCondition \
            WHERE julianday('now')-julianday(conditionDateTime) <= 2"

    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)
    row = cur.fetchone()

    if row["total_row_count"] > 0:
        total_row_count=float(row["total_row_count"])
        sql = "SELECT COUNT(*) AS rain_row_count FROM \
               weatherCondition \
               WHERE julianday('now')-julianday(conditionDateTime) <= 2 \
               AND (code<=18 or code==35 or code>=37)"
        cur = con.cursor() 
        cur.execute(sql)
        row = cur.fetchone()
        rain_row_count=float(row["rain_row_count"])

        multiplier = multiplier - (rain_row_count / total_row_count)


    return multiplier
# 6/5/2013 JRM returns True if the system is enabled and False if not
def IsSystemEnabled(con):
    sql = "SELECT *FROM irrigation_system"
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute(sql)
    row = cur.fetchone()

    if row["system_state"] == 0:
        system_enabled = False
    else:
        system_enabled = True

    return system_enabled


def InternetIsAvailable(url):
    try:
        response=urllib2.urlopen(url,timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

# 7/7/2016 JRM - use yahoo yql to query weather since pywapi doesn't work (stupid yahoo.com)
def ReadCurrentWeatherConditions():
    baseurl = "https://query.yahooapis.com/v1/public/yql?"

    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='hudsonville, mi')"

    yql_url = baseurl + urlencode({'q':yql_query}) + "&format=json"

    response = urllib.urlopen(yql_url).read()
    jsonResponse = json.loads(response.decode('utf-8'))
    return jsonResponse


def RecordCurrentWeatherConditions(con):
    # 7/7/2016 JRM - pwapi.get_weather_from_yahoo() stopped working in March 2016
    #currentWeather = pywapi.get_weather_from_yahoo('49426', units='')
    #conditionDateTime = datetime.strptime(currentWeather['condition']['date'],'%a, %d %b %Y %I:%M %p %Z')
    #temperature = currentWeather['condition']['temp']
    #code = currentWeather['condition']['code']

    jsonResponse = ReadCurrentWeatherConditions()
                                 
    # TODO add title, unitofmeasure, etc to weatherCondition
    title = jsonResponse['query']['results']['channel']['item']['title']
    dateTime = jsonResponse['query']['results']['channel']['item']['condition']['date']
    conditionDateTime = datetime.strptime(dateTime,'%a, %d %b %Y %I:%M %p %Z')
    weatherCode = int(jsonResponse['query']['results']['channel']['item']['condition']['code'])
    temperature = jsonResponse['query']['results']['channel']['item']['condition']['temp']
    unitofmeasure = jsonResponse['query']['results']['channel']['units']['temperature']
    conditions = jsonResponse['query']['results']['channel']['item']['condition']['text']

    text = jsonResponse['query']['results']['channel']['item']['forecast'][1]['text']
    high = jsonResponse['query']['results']['channel']['item']['forecast'][1]['high']
    low = jsonResponse['query']['results']['channel']['item']['forecast'][1]['low']
    date = jsonResponse['query']['results']['channel']['item']['forecast'][1]['date']
    day = jsonResponse['query']['results']['channel']['item']['forecast'][1]['day']
    forecast1 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, unitofmeasure, low, unitofmeasure)

    text = jsonResponse['query']['results']['channel']['item']['forecast'][2]['text']
    high = jsonResponse['query']['results']['channel']['item']['forecast'][2]['high']
    low = jsonResponse['query']['results']['channel']['item']['forecast'][2]['low']
    date = jsonResponse['query']['results']['channel']['item']['forecast'][2]['date']
    day = jsonResponse['query']['results']['channel']['item']['forecast'][2]['day']
    forecast2 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, unitofmeasure, low, unitofmeasure)

    text = jsonResponse['query']['results']['channel']['item']['forecast'][3]['text']
    high = jsonResponse['query']['results']['channel']['item']['forecast'][3]['high']
    low = jsonResponse['query']['results']['channel']['item']['forecast'][3]['low']
    date = jsonResponse['query']['results']['channel']['item']['forecast'][3]['date']
    day = jsonResponse['query']['results']['channel']['item']['forecast'][3]['day']
    forecast3 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, unitofmeasure, low, unitofmeasure)

    text = jsonResponse['query']['results']['channel']['item']['forecast'][4]['text']
    high = jsonResponse['query']['results']['channel']['item']['forecast'][4]['high']
    low = jsonResponse['query']['results']['channel']['item']['forecast'][4]['low']
    date = jsonResponse['query']['results']['channel']['item']['forecast'][4]['date']
    day = jsonResponse['query']['results']['channel']['item']['forecast'][4]['day']
    forecast4 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, unitofmeasure, low, unitofmeasure)

    text = jsonResponse['query']['results']['channel']['item']['forecast'][5]['text']
    high = jsonResponse['query']['results']['channel']['item']['forecast'][5]['high']
    low = jsonResponse['query']['results']['channel']['item']['forecast'][5]['low']
    date = jsonResponse['query']['results']['channel']['item']['forecast'][5]['date']
    day = jsonResponse['query']['results']['channel']['item']['forecast'][5]['day']
    forecast5 = "{} {} {} High: {} {} Low: {} {}".format(day, date, text, high, unitofmeasure, low, unitofmeasure)

    insertSql = "INSERT INTO \
                 weatherCondition (conditionDateTime, \
                 temperature, code) \
                 VALUES (?,?,?);"
    insertCur = con.cursor()
    insertCur.execute(insertSql, (conditionDateTime, temperature, weatherCode))
    con.commit()

def CheckRpiGpioRequest_OFF(con):
    # 3/9/2013 JRM - changed to have one record for both ON & OFF times so
    # I split the CheckRpiGpioRequest into separate OFF & ON functions
    # this one looks for any records in the rpiGpioRequest table where the offDateTime is now
    # turns the appropriate I/O OFF and updates the request as complete
    sql = "SELECT \
            rpiGpioRequest.id, \
            rpiGpioRequest.onDateTime, \
            rpiGpioRequest.offDateTime, \
            rpiGpioRequest.statusId, \
            rpiGpio.gpioName, \
            rpiGpio.gpioNumber, \
            status.shortName AS statusName, \
            rpiGpio.zoneId \
          FROM \
            rpiGpioRequest \
              JOIN rpiGpio ON rpiGpio.rpiGpioId=rpiGpioRequest.rpiGpioId \
              JOIN status ON status.statusId=rpiGpioRequest.statusId \
          WHERE \
            rpiGpioRequest.statusId=4 \
            AND offDateTime=strftime('%Y-%m-%d %H:%M:00','now','localtime');"
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)
       
    # read all the rows - should only be one but you never know
    rows = cur.fetchall()
    # need to fulfill the request
    for row in rows:
        ioid=int(row["gpioNumber"])
        zoneId = row["zoneId"]
        command="OFF"
        # execute the RPi GPIO command
        OutputCommand(ioid=ioid, zoneId=str(zoneId), command=command, con=con)
        # need to mark the request as complete
        requestId = row["id"]
        updateSql="UPDATE rpiGpioRequest SET statusId=2 WHERE id=?"
        updateCur = con.cursor()
        updateCur.execute(updateSql, (requestId, ))
        con.commit()     
 
def IsCurrentlyRaining(con):
    # 4/18/2013 JRM - returns True if it is raining or False if it is not
    sql = "SELECT MAX(id),temperature,code,conditionDateTime FROM weatherCondition"
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute(sql)
    row = cur.fetchone() 
    weather_code = int(row["code"])
    if weather_code<=18 or weather_code==35 or weather_code>=37:
      is_raining = True
    else:
      is_raining = False

    return is_raining

def CancelPendingRpiGpioRequests(con):
    # 4/18/2013 JRM update the rpiGpioRequest table to cancel all pending and active requests
    updateSql = "UPDATE rpiGpioRequest SET statusId=3 WHERE statusId IN (1,4)"
    updateCur = con.cursor()
    updateCur.execute(updateSql)
    con.commit()  

def CheckRpiGpioRequest_ON(con):
    # 3/9/2013 JRM - changed to have one record for both ON & OFF times so
    # I split the CheckRpiGpioRequest into separate OFF & ON functions
    # this one looks for any records in the rpiGpioRequest table where the onDateTime is now
    # turns the appropriate I/O ON and updates the request as active
    sql = "SELECT \
            rpiGpioRequest.id, \
            rpiGpioRequest.onDateTime, \
            rpiGpioRequest.offDateTime, \
            rpiGpioRequest.statusId, \
            rpiGpio.gpioName, \
            rpiGpio.gpioNumber, \
            status.shortName AS statusName, \
            rpiGpio.zoneId \
          FROM \
            rpiGpioRequest \
              JOIN rpiGpio ON rpiGpio.rpiGpioId=rpiGpioRequest.rpiGpioId \
              JOIN status ON status.statusId=rpiGpioRequest.statusId \
          WHERE \
            rpiGpioRequest.statusId=1 \
            AND onDateTime=strftime('%Y-%m-%d %H:%M:00','now','localtime');"
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)
       
    # read all the rows - should only be one but you never know
    rows = cur.fetchall()
    # need to fulfill the request
    for row in rows:
        ioid=int(row["gpioNumber"])
        zoneId = row["zoneId"]
        command="ON"
        # execute the RPi GPIO command
        OutputCommand(ioid=ioid, zoneId=str(zoneId), command=command, con=con)
        # need to mark the request as active
        #requestId=row["requestId"]
        requestId = row["id"]
        updateSql="UPDATE rpiGpioRequest SET statusId=4 WHERE id=?"
        updateCur = con.cursor()
        updateCur.execute(updateSql, (requestId, ))
        con.commit()         
            

class IrrigationControllerDaemon(daemon):
    def run(self):
        logging.basicConfig(filename='/var/www/data/irrigation/log/IrrigationController.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("IrrigationControllerDaemon.py Sqlite Version Starting Up")

        second_counter = 0
        minute_counter = 0

        con = lite.connect('/var/www/data/irrigation/irrigation/db/irrigation.db', 60)
        
        # 7/1/2013 JRM - check for internet availability before trying to read the weather conditions    
        if InternetIsAvailable('http://www.yahoo.com'):
            RecordCurrentWeatherConditions(con) 

        is_raining = IsCurrentlyRaining(con)
        system_enabled = IsSystemEnabled(con)
        
        if (not is_raining) and system_enabled:
            CheckIrrigationSchedule(con)
            CheckRpiGpioRequest_OFF(con)
            CheckRpiGpioRequest_ON(con)
        else:
            TurnAllOutputsOff(con)
            CancelPendingRpiGpioRequests(con)

        con.close()

        while True:
            con = lite.connect('/var/www/data/irrigation/irrigation/db/irrigation.db', 60)
            # sleep for 5 seconds
            time.sleep(5)        
            second_counter += 5

            # 4/18/2013 JRM - finally putting in logic to check if it is raining outside
            is_raining = IsCurrentlyRaining(con)

            # 6/5/2013 JRM - is the system enabled?
            system_enabled = IsSystemEnabled(con)

            if (not is_raining) and system_enabled:
                # check RpiGpioRequest happens every 5 seconds if it isn't raining
                # check if there is an OFF RPi GPIO request queued up for the current time
                CheckRpiGpioRequest_OFF(con)

                # check if there is an OFF RPi GPIO request queued up for the current time
                CheckRpiGpioRequest_ON(con)
            else:
                # it is raining so we need to cancel all active or pending RPi GPIO requests
                # and turn off all outputs
                TurnAllOutputsOff(con)
                CancelPendingRpiGpioRequests(con)

            # for keeping track of the seconds and minutes            
            if second_counter == 60:
              second_counter = 0
              minute_counter += 1
            
            # checking for irrigation schedule happens every 60 minutes
            # recording current weather conditions happens every 60 minutes
            if minute_counter == 60:
              CheckIrrigationSchedule(con)
              # 7/1/2013 JRM - check for internet availability before trying to read the weather conditions    
              if InternetIsAvailable('http://www.yahoo.com'):
                 RecordCurrentWeatherConditions(con)  
              minute_counter = 0
      
            # close database file
            con.close()


if __name__ == "__main__":
    irrigation_daemon = IrrigationControllerDaemon('/var/www/data/irrigation/run/IrrigationController.pid')
    con = lite.connect('/var/www/data/irrigation/irrigation/db/irrigation.db', 60)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            TurnAllOutputsOff(con)
            irrigation_daemon.start()
        elif 'stop' == sys.argv[1]:
            # 2/13/2013 JRM - turn all outputs off during stop
            TurnAllOutputsOff(con)
            irrigation_daemon.stop()
        elif 'restart' == sys.argv[1]:
            # 2/13/2013 JRM - turn all outputs off during restart
            TurnAllOutputsOff(con)
            irrigation_daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
