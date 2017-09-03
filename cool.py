#!/usr/bin/env python
import RPi.GPIO as GPIO
import os as OS
import time
from datetime import datetime

# -- SETUP -- 
log_file_path   = '/var/log/cputemplog/cputemp.log'
pin             = 8
temperature_max = 50
check_interval  = 60
log_interval    = 900
# -- SETUP END --

is_fan_on       = 0
last_check      = 0
temperature     = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

def saveToLogFile(line):
    global log_file_path, is_fan_on
    if OS.path.isfile(log_file_path) != True:
        text_file = open(log_file_path, "w")
    else:
        text_file = open(log_file_path, "a")
    text_file.write(line + '\n')
    text_file.close()

def systemCheck():
    global temperature, last_check, is_fan_on
    time_now = time.time()
    if (time_now >= last_check):
        last_check = time_now + log_interval
        ram_total,ram_use,ram_free = getRAMRaw()
        hdd_total,hdd_use,hdd_free = getDiskUseRaw()
        date_now  = datetime.now()
        line = "%s|%s|%s|%s|%s|%s|%s|%s|%s" % (date_now,temperature,is_fan_on,ram_total,ram_use,ram_free,hdd_total,hdd_use,hdd_free)
        saveToLogFile(line)

def temperatureCheck():
    global temperature, is_fan_on
    line = OS.popen('vcgencmd measure_temp').readline()
    temperature = line.replace("temp=","").replace("'C\n","")

    if (float(temperature) >= temperature_max) and (is_fan_on == 0):
        GPIO.output(pin, True)
        is_fan_on = 1
    if float(temperature) < temperature_max and is_fan_on == 1:
        GPIO.output(pin, False)
        is_fan_on = 0

def getRAMRaw():
    p = OS.popen('free')
    i = 0
    while True:
        line = p.readline()
        if i==1:
            return(line.split()[1:4])
        i += 1

def getDiskUseRaw():
    lines = OS.popen('df')
    i = 0
    for line in lines:
        if i == 1:
            return(line.split()[1:4])
        i += 1

try:
    while True:
        temperatureCheck()
        systemCheck()
        time.sleep(check_interval)

except KeyboardInterrupt:
    print("\nClosing...")
except:
    print("Unexpected error")
finally:
    print("\nCleaning GPIO")
    GPIO.cleanup()
