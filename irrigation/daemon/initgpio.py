#!/usr/bin/python
# -*- coding: utf-8 -*-
# 3/23/2016 JRM - initialize GPIO as GPIO.OUT and then turn them all OFF for use during boot
import sys
import datetime
import logging
import uuid
import RPi.GPIO as GPIO

def OutputCommand(ioid, command):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(ioid, GPIO.OUT)

    if command == "ON":
        GPIO.output(ioid, GPIO.HIGH)

    if command == "OFF":
        GPIO.output(ioid, GPIO.LOW)

OutputCommand(3,"OFF");
OutputCommand(5,"OFF");
OutputCommand(8,"OFF");
OutputCommand(7,"OFF");
OutputCommand(10,"OFF");
OutputCommand(11,"OFF");
OutputCommand(12,"OFF");
OutputCommand(21,"OFF");
OutputCommand(23,"OFF");
OutputCommand(24,"OFF");
OutputCommand(26,"OFF");
OutputCommand(29,"OFF");
OutputCommand(31,"OFF");
OutputCommand(32,"OFF");
OutputCommand(33,"OFF");
OutputCommand(35,"OFF");
OutputCommand(36,"OFF");
OutputCommand(37,"OFF");
OutputCommand(38,"OFF");
OutputCommand(40,"OFF");

