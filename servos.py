from __future__ import division
from threading import Thread

import helper
import time
import math
import sounds
import pwm
import gun
import random
import logging
from config import cfg

logger = logging.getLogger(__name__)

# Configure min and max servo pulse lengths
SERVO_MIN = int(cfg["servos"]["PWM_SERVO_MIN"])
SERVO_MAX = int(cfg["servos"]["PWM_SERVO_MAX"])
SERVO_SCAN_MIN = int(cfg["servos"]["SERVO_SCAN_MIN"])
SERVO_SCAN_MAX = int(cfg["servos"]["SERVO_SCAN_MAX"])
SERVO_SCAN_SPEED = int(cfg["servos"]["SERVO_SCAN_SPEED"])

SCAN_SWEEP_ENABLED = cfg.getboolean("servos", "SCAN_SWEEP_ENABLED")

# Pin configuration on the Adafruit board. Which pins are driving which servos?
PAN_PIN = cfg.getint("servos", "PWM_PAN_PIN")
TILT_PIN = cfg.getint("servos", "PWM_TILT_PIN")

"""
Current position of the servos, in degrees, within the range -90 to +90, with
zero being the midpoint.
"""


class XYCoord:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


position = XYCoord(0, 0)


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


scan_steps = generate_scan_curve(SERVO_SCAN_MIN, SERVO_SCAN_MAX,
                                 SERVO_SCAN_MAX-SERVO_SCAN_MIN)

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

    NOTE: This function blocks for a time dependent on SERVO_SPEED.
    """
    global scan_dirty
    scan_dirty = True

    p = int(helper.map(pan, -90, 90, SERVO_MIN, SERVO_MAX))
    t = int(helper.map(tilt, -90, 90, SERVO_MIN, SERVO_MAX))

    pwm.hat.set_pwm(PAN_PIN, 0, p)
    pwm.hat.set_pwm(TILT_PIN, 0, t)
    position.x = pan
    position.y = tilt


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
            if abs(pan_pos-position.x) < abs(scan_steps[best_pos]
                                             - position.x):
                best_pos = i
            i += 1
        current_scan_step = best_pos
    else:
        current_scan_step = (current_scan_step+1) % len(scan_steps)

    p = helper.map(scan_steps[current_scan_step], -90, 90,
                   SERVO_MIN, SERVO_MAX)

    if position.x != scan_steps[current_scan_step]:
        logger.debug("set_pwm({0})".format(int(p)))
        pwm.hat.set_pwm(PAN_PIN, 0, int(p))
        position.x = scan_steps[current_scan_step]
    else:
        logger.debug("x={0}, p={1}".format(position.x, p))

    scan_dirty = False


def init():
    # move the tilt servo from tilt=90 (full down) to tilt=0
    move_to(0, 80)
    for i in range(80, 0, -1):
        move_to(0, i)
        time.sleep(0.005)


def shutdown():
    logger.info("shutting down from {0},{1}"
                .format(position.x, position.y))

    x = position.x
    inc = 1 if x < 0 else -1
    for i in range(0, abs(x)):
        logger.debug("x={0}".format(x+(i*inc)))
        move_to(x+(i*inc), position.y)
        time.sleep(0.005)

    for i in range(position.y, 80):
        logger.debug("y={0}".format(i))
        move_to(position.x, i)
        time.sleep(0.005)


class ScanWorker(Thread):
    paused = False
    stopped = False

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.paused = False
        self.stopped = False
        pinging = False
        sounds.play(sounds.TURRET_ACTIVATED, sounds.BLOCKING)
        while not self.stopped:
            if SCAN_SWEEP_ENABLED and not self.paused:
                scan()
                t = int(round(time.time())) % 3
                if t == 0 and not pinging:
                    pinging = True
                    sounds.play(sounds.SCAN, sounds.NON_BLOCKING)
                elif t != 0:
                    pinging = False

            time.sleep(SERVO_SCAN_SPEED / 1000)

        sounds.play(sounds.SHUTTING_DOWN, sounds.BLOCKING)

    def pause(self, state=True):
        self.paused = state

    def stop(self):
        self.stopped = True


if __name__ == "__main__":

    def calibrate():
        """
        Aim calibration.

        Move the servos in a grid pattern, firing the laser, taking a
        picture and recording it to disk.

        From the photo output, we will be able to determine the relative servo
        angle for each pixel in the captured image.
        """

        import picamera
        # import os

        camera = picamera.PiCamera()
        # with PiCamera() as camera:
        camera.resolution = (1024, 768)
        # camera.start_preview()
        # Camera warm-up time
        # time.sleep(2)

        gun.laser(0)  # laser ON
        # pwm.hat.set_pwm(LASER_PIN, 0, 4095)

        for y in range(-25, 30, 5):
            for x in range(-45, 45, 5):

                file_name = 'images/x%d_y%d.jpg' % (x, y)
                # if((not os.path.isfile(file_name)) or
                #         os.stat(file_name).st_size == 0):
                move_to(x, y)
                time.sleep(0.3)
                logger.info(file_name)
                # sounds.play(sounds.SCAN2, sounds.NON_BLOCKING)

                camera.capture(file_name)
                time.sleep(0.2)

        gun.laser(0.01)  # laser OFF
        # pwm.hat.set_pwm(LASER_PIN, 0 , 0)

        camera.close()

        move_to(0, 0)

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
        val = input("Input Command (enter to fire, "
                    "'C' to calibrate, "
                    "'Q' to quit.): ")

        if(val.lower() == "q"):
            break
        elif(val.lower() == "c"):
            scanner.pause()
            calibrate()
            scanner.pause(False)
        elif(val == ""):
            scanner.pause()

            s = random.choice([
                sounds.TURRET_FIRE,
                sounds.TURRET_FIRE_2,
                sounds.TURRET_FIRE_3
            ])
            sounds.play(s, sounds.NON_BLOCKING)
            gun.laser(0.2)

            scanner.pause(False)
        else:
            logger.warn("Unrecognized command: '{0}'".format(val))

    scanner.stop()

    logger.info("Shutting down.")
    shutdown()
