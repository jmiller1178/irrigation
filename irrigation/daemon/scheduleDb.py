#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import time
import sys
import datetime
import logging

logging.basicConfig(filename='scheduleDb.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info("scheduleDb.py Starting Up")
# This query will return the record(s) for turning on right now 
        # right now is defined as matching the day of the week
        # and the hour and the minute and the zone is enabled and the schedule is enabled
        sql = "SELECT \
              schedule.displayName AS scheduleDisplayName,\
              zone.displayName AS zoneDisplayName,\
              irrigationSchedule.zoneId, \
              irrigationSchedule.startTime, \
              irrigationSchedule.endTime,\
              rpiGpio.id AS rpiGpioId, \
              rpiGpio.gpioName,\
              rpiGpio.gpioNumber\
            FROM\
              irrigationSchedule \
                JOIN zoneRpiGpio ON irrigationSchedule.zoneId=zoneRpiGpio.zoneId\
                JOIN rpiGpio ON zoneRpiGpio.rpiGpioId=rpiGpio.id \
                JOIN schedule ON irrigationSchedule.scheduleId=schedule.id\
                JOIN zone ON irrigationSchedule.zoneId=zone.id\
            WHERE\
              weekDayId=DAYOFWEEK(now())\
              AND HOUR(startTime)=HOUR(now())\
              AND MINUTE(startTime)=MINUTE(now())\
              AND zone.enabled=1\
              AND schedule.enabled=1"

        while True:
            # run forever  - wakes up every minute to re run the above query
            # Open database connection
            con = mdb.connect("localhost","icappuser","icappuser","irrigationcontroller" )
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)

            if cur.rowcount > 0:
                # should be only one row read but you never know
                rows = cur.fetchall()
                # need to do an INSERT statement into the rpiGpioRequest table
                for row in rows:
                    rpiGpioId=row["rpiGpioId"]
                    today = datetime.date.today()
                    # TODO there has to be a better way than this to build a date/time string to insert
                    startDateTime=str(today) + ' ' + str(row["startTime"])
                    endDateTime=str(today) + ' ' + str(row["endTime"])

                    logging.info("Scheduled request found rpiGpioId: %s startDateTime: %s endDateTime: %s",  rpiGpioId,  startDateTime,  endDateTime)

                    # this is the INSERT statement to create a request record in the rpiGpioRequest table
                    insertSql = "INSERT INTO rpiGpioRequest(rpiGpioId, requestTypeId, requestDateTime,statusId)\
                     VALUES(%s,%s,%s,%s)"
                    insertCur = con.cursor()
                    # insert the ON request
                    insertCur.execute(insertSql,(rpiGpioId,1,startDateTime, 1))
                    # insert the OFF request
                    insertCur.execute(insertSql, (rpiGpioId, 0, endDateTime, 1))

                    con.commit()            
                # sleep for a minute
                con.close()
                time.sleep(60)    
   
  
