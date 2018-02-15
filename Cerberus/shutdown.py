#!/usr/bin/env python
import RPi.GPIO as GPIO
import subprocess

SHUTDOWN_PIN = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(SHUTDOWN_PIN, GPIO.FALLING)

subprocess.call(['shutdown', '-h', 'now'], shell=False)
