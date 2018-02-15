import RPi.GPIO as GPIO
import sounds
import time
import random

TRIGGER_PIN = 5
USE_SHOT_COUNTER = True
MAGAZINE_SIZE = 100
TRIGGER_DOWN_MILLIS = 50  # time to hold the trigger down.

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)

safety_on = False
shot_count = 0


def make_safe(state=True):
    global safety_on
    safety_on = state


def reset():
    global shot_count
    shot_count = 0


def shoot():
    """
    Shoots the gun once, holding down the trigger for TRIGGER_DOWN_MILLIS
    milliseconds (blocking call).
    """
    global shot_count

    if(not safety_on):
        if(shot_count < MAGAZINE_SIZE or not USE_SHOT_COUNTER):
            GPIO.output(TRIGGER_PIN, GPIO.HIGH)
            shot_count += 1
            time.sleep(TRIGGER_DOWN_MILLIS / 1000.0)
            print(MAGAZINE_SIZE - shot_count)
            # stop shooting. This part's important.
            GPIO.output(TRIGGER_PIN, GPIO.LOW)
            return True
        else:
            sounds.play(random.choice([
                sounds.CLICK,
                sounds.CLICK_2,
                sounds.CLICK_3,
                sounds.CLICK_4,
                sounds.CLICK_5,
                sounds.CLICK_6,
            ]))
            print("Click.")
            GPIO.output(TRIGGER_PIN, GPIO.LOW)
            return False
    else:
        # make damn sure.
        GPIO.output(TRIGGER_PIN, GPIO.LOW)
        return False


if (__name__ == "__main__"):
    """Test the gun. Very dangerous."""

# fire the gun once.
    shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN_WAV)

# fire the gun n times.
    for x in range(0, 3):
        shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN_WAV)

# fire the gun while empty.
    shot_count = MAGAZINE_SIZE
    for x in range(0, 3):
        shoot()
        time.sleep(1)

# reset the shot count.
    reset()
    sounds.play(sounds.SCAN_WAV)

# make safe.
    make_safe()
    time.sleep(1)
    sounds.play(sounds.SCAN_WAV)

# attempt to fire the gun once, while safety is on.
    shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN_WAV)

# make unsafe.
    make_safe(False)
    time.sleep(1)
    sounds.play(sounds.SCAN_WAV)
