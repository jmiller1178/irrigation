#!/usr/bin/python
# -*- coding: utf-8 -*-
# 1/27/2013 JRM - changed to use SQLite instead of MySql due to perfromance issues
#
import sqlite3 as lite
import datetime
import logging
import sys
import time
import RPi.GPIO as GPIO
from daemon import Daemon
import logging

def OutputCommand(ioid, command):
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)

  GPIO.setup(ioid, GPIO.OUT)

  if command == "ON":
    GPIO.output(ioid, GPIO.HIGH)

  if command == "OFF":
    GPIO.output(ioid, GPIO.LOW)

def TurnAllOutputsOff():
    sql = "SELECT * FROM rpiGpio;"
    con = lite.connect('/usr/share/irrigationController/irrigationController.db', 60)
    #cur = con.cursor(mdb.cursors.DictCursor)
    con.row_factory = lite.Row
    cur = con.cursor() 
    cur.execute(sql)

    rows = cur.fetchall()
    # need to fulfill the request
    for row in rows:
        ioid = row["gpioNumber"]
        OutputCommand(ioid=ioid, command="OFF")
    con.close()
    
class RpiGpioDaemon(Daemon):
    def run(self):
        logging.basicConfig(filename='/var/log/rpiGpioDaemon.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("rpiGpioDaemon.py Sqlite Version Starting Up")
        
        #turn off all outputs to start
        TurnAllOutputsOff()

       # This query will return the record(s) for turning on right now 
       # right now is defined as matching the day of the week
       # and the hour and the minute and the zone is enabled and the schedule is enabled
        while True:
            sql = "SELECT \
             requestId,\
             requestTypeId,\
             requestDateTime,\
             statusId,\
             rpiGpio.gpioName,\
             rpiGpio.gpioNumber,\
             status.shortName AS statusName,\
             requestType.shortName As requestName\
           FROM  \
             rpiGpioRequest\
                JOIN rpiGpio ON rpiGpio.id=rpiGpioRequest.rpiGpioId\
                JOIN status ON status.id=rpiGpioRequest.statusId\
                JOIN requestType ON requestType.id=rpiGpioRequest.requestTypeId\
           WHERE\
             rpiGpioRequest.statusId=1\
             AND requestDateTime=strftime('%Y-%m-%d %H:%M:00','now','localtime');"
                        #AND requestDateTime=DATE_FORMAT(now(),'%Y-%m-%d %H:%i:00')"
            # run forever  - wakes up every 10 seconds to re run the above query    
            # Open database connection - the 60 is timeout seconds in case the database is locked by another process
            #con = mdb.connect("localhost","icappuser","icappuser","irrigationcontroller" )
            con = lite.connect('/usr/share/irrigationController/irrigationController.db', 60)
            #cur = con.cursor(mdb.cursors.DictCursor)
            con.row_factory = lite.Row
            cur = con.cursor() 
            cur.execute(sql)
           
            # read all the rows - should only be one but you never know
            rows = cur.fetchall()
            # need to fulfill the request
            for row in rows:
                ioid=int(row["gpioNumber"])
                command=row["requestName"]
                # execute the RPi GPIO command
                OutputCommand(ioid=ioid,  command=command)
                
                # need to mark the request as completed
                requestId=row["requestId"]
                logging.info("RPi GPIO Request Found %s %s %s", row["gpioNumber"],command, requestId)
                #updateSql="UPDATE rpiGpioRequest SET statusId=2 WHERE requestId=%s"
                updateSql="UPDATE rpiGpioRequest SET statusId=2 WHERE requestId=?"
                updateCur = con.cursor()
                updateCur.execute(updateSql, (requestId, ))
                con.commit()         
                time.sleep(1) #new added this on 1/30/2013 to allow some setting time for the valve
            
            # close the connection and sleep for 10 seconds    
            con.close()
            time.sleep(10)
            
if __name__ == "__main__":
    daemon = RpiGpioDaemon('/var/run/RpiGpioDaemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            TurnAllOutputsOff()
            logging.info("rpiGpioDaemon.py Shutting Down")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
        

