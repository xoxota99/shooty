from __future__ import division

import RPi.GPIO as GPIO
import servos
import vision
import sounds
import gun


oldButtonState1 = True
shutdown = False


def handle_shutdown_button():
    """
    Check the state of the shutdown button, debounce the button, and set the
    shutdown flag to the appropriate boolean value. When shutdown = True,
    the main loop will exit.
    """

    global oldButtonState1
    global shutdown
    # grab the current button state
    buttonState1 = GPIO.input(SHUTDOWN_PIN)
    # debounce
    if buttonState1 != oldButtonState1 and not buttonState1:
        # Button was down, and now it's up. Do your thing.
        shutdown = True

    oldButtonState1 = buttonState1

# ============


if (__name__ == "__main__"):
    """Main loop"""

    # We don't mess with the GPIO unless this script is the main script.
    SHUTDOWN_PIN = 5
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    servos.move_to(0, 0)
    sounds.play(sounds.STARTUP_WAV)
    gun.laser()

    while(not shutdown):
        handle_shutdown_button()

        if(vision.acquireTarget()):
            if(not vision.is_friendly):
                # We have a target, and no friend detected
                sounds.play(sounds.TARGET_ACQUIRED_WAV, False)
                servos.move_to(vision.target.x, vision.target.y)
                gun.shoot()

                while vision.acquireTarget():
                    servos.move_to(vision.target.x, vision.target.y)
                    if(not vision.is_friendly):
                        gun.shoot()

                sounds.play(sounds.TARGET_LOST_WAV, False)
            else:
                servos.move_to(vision.target.x, vision.target.y)
                # Friend detected.
                sounds.play(sounds.HELLO_FRIEND_WAV)
        else:
            sounds.play(sounds.SCAN_WAV)

    sounds.play(sounds.SHUTTING_DOWN_WAV)
