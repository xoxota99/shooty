from __future__ import division

import RPi.GPIO as GPIO
import servos
import vision
import sounds
import gun
import time


if (__name__ == "__main__"):
    """Main loop"""

    # We don't mess with the GPIO unless this script is the main script.

    servos.move_to(0, 0)
    sounds.play(sounds.STARTUP_WAV, False)

    while(True):
        if(vision.acquire_target()):
            servos.move_to(vision.target.x, vision.target.y)
            if(not vision.target.friendly):
                # We have a target, and no friend detected
                sounds.play(sounds.TARGET_ACQUIRED_WAV, False)
                gun.shoot()

                while vision.acquire_target():
                    servos.move_to(vision.target.x, vision.target.y)
                    if(not vision.target.friendly):
                        gun.shoot()

                sounds.play(sounds.TARGET_LOST_WAV, False)
            else:
                # Friend detected.
                sounds.play(sounds.HELLO_FRIEND_WAV, False)
        else:
            if (time.time() * 1000) % 3 == 0:
                sounds.play(sounds.SCAN_WAV, False)
            servos.scan()

    # shut down.
    sounds.play(sounds.SHUTTING_DOWN_WAV, False)
