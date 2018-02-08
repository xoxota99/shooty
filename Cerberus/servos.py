from __future__ import division
import math
import time
import Adafruit_PCA9685
# import logging

# logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

# Configure min and max servo pulse lengths
SERVO_MIN = 150  # Min pulse length out of 4096
SERVO_MAX = 600  # Max pulse length out of 4096

# Pin configuration on the Adafruit board. Which pins are driving which servos?
PAN_PIN = 0
TILT_PIN = 1


def move_to(pan, tilt=0):
    """
    Move to specific angles (in degrees) in the pan and tilt head. Range is -90
    to 90 degrees.
    params:
        - pan : degrees angle of the pan servo, from -90 degrees (full left) to
                90 degrees (full right).
        - tilt: degrees angle of the tilt servo, from -90 degrees (full down)
                to 90 degrees (full up).

    NOTE: This function is non-blocking. This means the physical servo may
    continue to move to it's new setpoint after this function has returned.
    """
    p = math.map(pan, -90, 90, SERVO_MIN, SERVO_MAX)
    t = math.map(tilt, -90, 90, SERVO_MIN, SERVO_MAX)
    pwm.set_pwm(0, PAN_PIN, p)
    pwm.set_pwm(0, TILT_PIN, t)


if __name__ == "__main__":
    """test the servos."""

    print('Moving servo on channel 0/1, press Ctrl-C to quit...')
    while True:
        # Move servo on channel O between extremes.
        pwm.set_pwm(0, PAN_PIN, SERVO_MIN)
        pwm.set_pwm(0, TILT_PIN, SERVO_MIN)
        time.sleep(1)
        pwm.set_pwm(0, TILT_PIN, SERVO_MAX)
        time.sleep(1)
        pwm.set_pwm(0, PAN_PIN, SERVO_MAX)
        time.sleep(1)
        pwm.set_pwm(0, TILT_PIN, SERVO_MIN)
        time.sleep(1)
