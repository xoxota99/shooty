#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import subprocess

RESET_PIN = 5
SLEEP_CYCLE_SEC = 0.100

# we will use the pin numbering to match the pins on the Pi, instead of the
# GPIO pin outs (makes it easier to keep track of things)

GPIO.setmode(GPIO.BOARD)

# use the same pin that is used for the reset button (one button to rule them
# all!)
GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

oldButtonState1 = True

while True:
    # grab the current button state
    buttonState1 = GPIO.input(RESET_PIN)

    # debounce
    if buttonState1 != oldButtonState1 and not buttonState1:
        # Button was down, and now it's up. Do your thing.
        subprocess.call("shutdown -h now", shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    oldButtonState1 = buttonState1
    time.sleep(SLEEP_CYCLE_SEC)
