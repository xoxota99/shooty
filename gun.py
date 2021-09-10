import sounds
import time
import random
import pwm
import logging
from config import cfg

logger = logging.getLogger(__name__)

PWM_TRIGGER_PIN = cfg.getint("gun", "PWM_TRIGGER_PIN")
PWM_LASER_PIN = cfg.getint("gun", "PWM_LASER_PIN")

USE_SHOT_COUNTER = cfg.getboolean("gun", "USE_SHOT_COUNTER")
MAGAZINE_SIZE = cfg.getint("gun", "MAGAZINE_SIZE")

# time to hold the trigger down.
TRIGGER_DOWN_MILLIS = cfg.getint("gun", "TRIGGER_DOWN_MILLIS")
GUN_ENABLED = cfg.getboolean("gun", "GUN_ENABLED")

safety_on = False
shot_count = 0


def make_safe(state=True):
    global safety_on
    safety_on = state


def reset():
    global shot_count
    shot_count = 0


def laser(seconds=0):
    """
    Fire the laser for the provided number of seconds, make a "pew pew" noise.
    If <seconds> is greater than zero, turn off the laser after that many
    seconds. (blocking call)
    """
    pwm.hat.set_pwm(PWM_LASER_PIN, 0, 4095)

    if seconds > 0:
        time.sleep(seconds)
        pwm.hat.set_pwm(PWM_LASER_PIN, 0, 0)


def shoot(trigger_down_millis=TRIGGER_DOWN_MILLIS):
    """
    Shoots the gun once, holding down the trigger for TRIGGER_DOWN_MILLIS
    milliseconds (blocking call).
    """
    global shot_count

    if GUN_ENABLED:
        if(not safety_on):
            if(shot_count < MAGAZINE_SIZE or not USE_SHOT_COUNTER):
                pwm.hat.set_pwm(PWM_TRIGGER_PIN, 0, 4095)
                shot_count += 1
                time.sleep(float(trigger_down_millis) / 1000.0)
                logger.debug("shots remaining: {}"
                             .format(MAGAZINE_SIZE - shot_count))
                # stop shooting. This part's important.
                pwm.hat.set_pwm(PWM_TRIGGER_PIN, 0, 0)
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
                logger.debug("Click.")
                pwm.hat.set_pwm(PWM_TRIGGER_PIN, 0, 0)
                return False
        else:
            # make damn sure.
            pwm.hat.set_pwm(PWM_TRIGGER_PIN, 0, 0)
            return False
    else:
        logger.info("Gun disabled in config. pew pew. (☞ ͡° ͜ʖ ͡°)☞")
        s = random.choice([
            sounds.TURRET_FIRE,
            sounds.TURRET_FIRE_2,
            sounds.TURRET_FIRE_3
        ])
        sounds.play(s, sounds.NON_BLOCKING)
        time.sleep(float(trigger_down_millis) / 1000.0)


if (__name__ == "__main__"):
    """Test fire the gun, wherever it's currently aimed. Very dangerous."""

# fire the gun once.
    shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN)

# fire the gun n times.
    for _ in range(0, 3):
        shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN)

# fire the gun while empty.
    shot_count = MAGAZINE_SIZE
    for x in range(0, 3):
        shoot()
        time.sleep(1)

# reset the shot count.
    reset()
    sounds.play(sounds.SCAN)

# make safe.
    make_safe()
    time.sleep(1)
    sounds.play(sounds.SCAN)

# attempt to fire the gun once, while safety is on.
    shoot()
    time.sleep(1)
    sounds.play(sounds.SCAN)

# make unsafe.
    make_safe(False)
    time.sleep(1)
    sounds.play(sounds.SCAN)
