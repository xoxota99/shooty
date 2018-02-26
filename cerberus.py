from __future__ import division

import servos
import vision
import sounds
import gun
import random
import logging
from config import cfg

logger = logging.getLogger(__name__)

locked = False
panner = None


def transform(x, y):
    """
    Transform the X/Y coordinates of the target centroid within the camera
    frame into Servo pan/tilt values in degrees.
    """

    return x, y


def target_acquired_callback(target, frame):
    """
    Called from the vision processor:
        - when it discovers a target.
        - continuously, as a target is still in frame.
    """
    global locked
    global panner

    if not locked:
        # New target.
        logger.info("Target Acquired: ", target)
        panner.pause()
        if target.friendly:
            s = random.choice({
                sounds.HELLO_FRIEND,
                sounds.HELLO_FRIEND_2
            })
            sounds.play(s, False)
        else:
            sounds.play(sounds.TARGET_ACQUIRED, False)

        locked = True

    # aim for the center of mass
    (sx, sy) = transform(int(target.x + target.w/2), int(target.y+target.h/2))

    servos.move_to(sx, sy)
    if not vision.target.friendly:
        gun.shoot()


def target_lost_callback(target, frame):
    global locked
    global panner
    """
    Called from the vision processor:
        - when a target is lost.
        - continuously, as there is no target in frame.
    """
    if locked:
        # we had a target, now we don't.
        logger.info("Target Lost: ", target)
        panner.pause(False)
        if not target.friendly:
            sounds.play(sounds.TARGET_LOST, False)
        locked = False


"""Main sentry program"""
if (__name__ == "__main__"):
    logger.info("initializing servos")
    servos.init()

    logger.info("moveto(0,0)")
    servos.move_to(0, 0)

    # "panner" is a thread that just moves the pan servo back and forth, in a
    # "scanning for intruders" sort of behavior. It's purely cosmetic, but
    # helps us remember that the bloody thing is on and dangerous.
    panner = servos.ScanWorker()
    panner.daemon = True
    logger.info("starting motor pan/tilt thread.")
    panner.start()

    # "scanner" is the thread that's running the vision main loop and video
    # processing.
    scanner = vision.VisionWorker()
    scanner.daemon = True
    logger.info("starting vision thread.")
    scanner.start(target_acquired_callback=target_acquired_callback,
                  target_lost_callback=target_lost_callback)

    while not scanner.stopped:
        val = input("Input Command (enter to fire, "
                    "'Q' to quit.): ")

        if(val.lower() == "q"):
            break
        elif(val == ""):
            scanner.pause()

            gun.shoot()

            scanner.pause(False)
        else:
            logger.warn("Unrecognized command: '{0}'".format(val))

    scanner.stop()
    panner.stop()
    servos.shutdown()
