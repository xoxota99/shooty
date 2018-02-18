from __future__ import division
from threading import Thread

import helper
import time
import Adafruit_PCA9685
import math
import logging
import sounds

logging.basicConfig(level=logging.INFO)

# Set frequency to 50hz, good for servos.
PWM_FREQ = 50

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

pwm.set_pwm_freq(PWM_FREQ)

# Configure min and max servo pulse lengths
SERVO_MIN = 151
SERVO_MAX = 450

# Pin configuration on the Adafruit board. Which pins are driving which servos?
PAN_PIN = 0
TILT_PIN = 1

"""
Position of the servos, in degrees, within the range -90 to +90, with
zero being the midpoint.
"""
position = {
    'x': 0,
    'y': 0
}


def generate_scan_curve(min_value, max_value, steps):
    """
    generate an array of step values along a sine curve, from min, to max,
    and back to min.
    """
    retval = []

    half_range = (max_value - min_value)/2
    for i in range(1, steps):
        val = int(min_value + half_range + math.sin(math.pi*i/(steps/2))
                  * half_range)

        retval.append(val)

    return retval


scan_steps = generate_scan_curve(-90, 90, 180)

current_scan_step = 0
scan_dirty = True


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
    global scan_dirty
    scan_dirty = True

    p = helper.map(pan, -90, 90, SERVO_MIN, SERVO_MAX)
    t = helper.map(tilt, -90, 90, SERVO_MIN, SERVO_MAX)

    # pCurve = helper.generateCurve(position['x'], p, SERVO_MAX_SPEED)
    # tCurve = helper.generateCurve(position['y'], t, SERVO_MAX_SPEED)

    pwm.set_pwm(PAN_PIN, 0, p)
    pwm.set_pwm(TILT_PIN, 0, t)
    position['x'] = pan
    position['y'] = tilt


def scan():
    global scan_dirty
    global current_scan_step

    if scan_dirty:
        # Where is the pan servo right now? Recalculate the closest step,
        # according to the internal state (which might not match the physical
        # state).
        best_pos = 0
        i = 0
        for pan_pos in scan_steps:
            if abs(pan_pos-position['x']) < abs(scan_steps[best_pos]
                                                - position['x']):
                best_pos = i
            i += 1
            logging.debug("scan: {0}".format(i))
        current_scan_step = best_pos
    else:
        current_scan_step = (current_scan_step+1) % len(scan_steps)

    p = helper.map(scan_steps[current_scan_step], -90, 90,
                   SERVO_MIN, SERVO_MAX)

    if position['x'] != scan_steps[current_scan_step]:
        logging.debug("set_pwm({0})".format(int(p)))
        pwm.set_pwm(PAN_PIN, 0, int(p))
        position['x'] = scan_steps[current_scan_step]
    else:
        logging.debug("x={0}, p={1}".format(position['x'], p))

    scan_dirty = False


def init():
    # move the tilt servo from tilt=90 (full down) to tilt=0
    move_to(0, 80)
    for i in range(80, 0, -1):
        move_to(0, i)
        time.sleep(0.005)


def shutdown():
    print("shutting down from {0},{1}".format(position['x'], position['y']))

    x = position['x']
    inc = 1 if x < 0 else -1
    for i in range(0, abs(x)):
        # print("x={0}".format(x+(i*inc)))
        move_to(x+(i*inc), position['y'])
        time.sleep(0.005)

    for i in range(position['y'], 80):
        # print("y={0}", i)
        move_to(position['x'], i)
        time.sleep(0.005)


class ScanWorker(Thread):
    paused = False
    stopped = False

    def __init__(self):
        print("ScanWorker.__init__()")
        Thread.__init__(self)

    def run(self):
        sounds.play(sounds.TURRET_ACTIVATED, False)
        while not self.stopped:
            if not self.paused:
                scan()
                time.sleep(0.03)
        sounds.play(sounds.SHUTTING_DOWN, False)

    def pause(self, state=True):
        self.paused = state

    def stop(self):
        self.stopped = True


if __name__ == "__main__":

    LASER_PIN = 2

    def shoot():
        pwm.set_pwm(LASER_PIN, 0, 4095)
        print("pew!")
        sounds.play(sounds.PEW, False)
        time.sleep(0.2)
        pwm.set_pwm(LASER_PIN, 0, 0)

    """
    Test the servos.

    Usage: servos.py [<pin#> <angle_degrees>]
    """
    init()
    move_to(0, 0)

    scanner = ScanWorker()
    scanner.daemon = True
    scanner.start()

    while True:
        val = raw_input("Input Command (enter to fire, 'Q' to quit.): ")
        if(val.lower() == "q"):
            break
        elif(val == ""):
            scanner.pause()
            shoot()
            scanner.pause(False)
        else:
            print("Unrecognized command: '{0}'".format(val))

    scanner.stop()

    print("Shutting down.")
    shutdown()
