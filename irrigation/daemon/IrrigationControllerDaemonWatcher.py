#!/usr/bin/python
# -*- coding: utf-8 -*-
# 5/18/2013 JRM - 2nd Daemon process to watch the IrrigationControllerDaemon and restart it if it stops
#
from daemon import Daemon
import time
import sys
from datetime import datetime, date, timedelta
import logging
import uuid
import pywapi
from os.path import exists                     
import subprocess

class IrrigationControllerDaemonWatcher(Daemon):
    def run(self):
        logging.basicConfig(filename='/var/log/IrrigationControllerWatcher.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("IrrigationControllerDaemonWatcher.py Starting Up")

        minute_counter = 0
        pid_file_name='/var/run/IrrigationController.pid'

        while True:
            if exists(pid_file_name) == False:
                args = ['/etc/init.d/irrigationController', 'start']
                subprocess.call(args) 
            # sleep for 60 seconds
            time.sleep(60)   

if __name__ == "__main__":
    daemon = IrrigationControllerDaemonWatcher('/var/run/IrrigationControllerWatcher.pid')
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
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
