#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import MySQLdb as mdb
import time
import sys
import datetime
import logging
import uuid

logging.basicConfig(filename='/tmp/scheduleDb.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info("scheduleDb.py Starting Up")
# This query will return the record(s) for turning on right now 
# right now is defined as matching the day of the week
# and the hour and the minute and the zone is enabled and the schedule is enabled
sql = "SELECT \
    schedule.displayName AS scheduleDisplayName,\
    zone.displayName AS zoneDisplayName,\
    irrigationSchedule.zoneId, \
    irrigationSchedule.startTime,\
    irrigationSchedule.endTime,\
    rpiGpio.id AS rpiGpioId, \
    rpiGpio.gpioName,\
    rpiGpio.gpioNumber\
  FROM\
    irrigationSchedule \
    JOIN zoneRpiGpio ON irrigationSchedule.zoneId=zoneRpiGpio.zoneId\
    JOIN rpiGpio ON zoneRpiGpio.rpiGpioId=rpiGpio.id\
    JOIN schedule ON irrigationSchedule.scheduleId=schedule.id\
    JOIN zone ON irrigationSchedule.zoneId=zone.id\
  WHERE\
    weekDayId=(strftime('%w','now','localtime')+1)\
    AND substr(startTime,0,3)=strftime('%H','now','localtime')\
    AND substr(startTime,4,2)=strftime('%M','now','localtime')\
    AND zone.enabled=1\
    AND schedule.enabled=1;"

while True:
    # run forever  - wakes up every minute to re run the above query
    # Open database connection
       #con = mdb.connect("localhost","icappuser","icappuser","irrigationcontroller" )
    con = lite.connect('/usr/share/irrigationController/irrigationController.db', 60)
    #cur = con.cursor(mdb.cursors.DictCursor)
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)

    rows = cur.fetchall()
    # need to do an INSERT statement into the rpiGpioRequest table
    for row in rows:
        
        rpiGpioId=row["rpiGpioId"]
        today = datetime.date.today()
        startDateTime=str(today) + ' ' + str(row["startTime"])
        endDateTime=str(today) + ' ' + str(row["endTime"])

        #formulate a query to check if there is already a record written for the rpiGpioId, requestTypeId and requestDateTime
        selectSql = "SELECT \
                  COUNT(requestId) AS cnt \
                FROM \
                  rpiGpioRequest \
                WHERE \
                  rpiGpioId=? \
                  AND requestTypeId=? \
                  AND requestDateTime=?;"                
		
        selectCur = con.cursor()
        selectCur.execute(selectSql,(rpiGpioId,1,startDateTime))
        selectRow = selectCur.fetchone()
		
        if selectRow["cnt"] == 0: # no record is found so we need to write the pair for ON & OFF
            # this is the INSERT statement to create a request record in the rpiGpioRequest table
            #insertSql = "INSERT INTO rpiGpioRequest(rpiGpioId, requestTypeId, requestDateTime,statusId)\
            #VALUES(%s,%s,%s,%s)"
            insertSql = "INSERT INTO rpiGpioRequest(requestId, rpiGpioId, requestTypeId, requestDateTime,statusId)\
                VALUES(?,?,?,?,?)"
            insertCur = con.cursor()
            # insert the ON request
            requestId = str(uuid.uuid4())
            insertCur.execute(insertSql,(requestId,  rpiGpioId,1,startDateTime, 1))
            # insert the OFF request
            requestId = str(uuid.uuid4())
            insertCur.execute(insertSql, (requestId,  rpiGpioId, 0, endDateTime, 1))

            con.commit()            
    # sleep for a minute
    con.close()
    time.sleep(15)    

  
