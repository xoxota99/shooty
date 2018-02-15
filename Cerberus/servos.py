from __future__ import division
import helper
import time
import Adafruit_PCA9685
import math

# Set frequency to 50hz, good for servos.
PWM_FREQ = 50

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

pwm.set_pwm_freq(PWM_FREQ)

# Configure min and max servo pulse lengths
SERVO_MIN = 150
SERVO_MAX = 600

# Pin configuration on the Adafruit board. Which pins are driving which servos?
PAN_PIN = 0
TILT_PIN = 1

position = {
    'x': 0,
    'y': 0
}


def generate_scan_curve(min, max, steps):
    """
    generate an array of step values along a sine curve, from min, to max,
    and back to min.
    """
    retval = []
    halfRange = (max - min) / 2
    for i in range(1, steps):
        retval.append(min + halfRange + math.sin(math.pi*i/(steps-2))
                      * halfRange)
    return retval


scan_steps = generate_scan_curve(-90, 90, 180)
current_scan_step = 0
scan_dirty = True


def set_servo_pulse(channel, pulse):
    """
    Helper function to make setting a servo pulse width simpler.
    """
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= PWM_FREQ       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


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

    pCurve = helper.generateCurve(position['x'], p, SERVO_MAX_SPEED)
    tCurve = helper.generateCurve(position['y'], t, SERVO_MAX_SPEED)

    set_servo_pulse(PAN_PIN, p)
    set_servo_pulse(TILT_PIN, t)
    position['x'] = p
    position['y'] = t


def scan():
    global scan_dirty
    global current_scan_step

    if scan_dirty:
        # Where is the pan servo right now? Rcalculate the closest step,
        # according to the internal state (which might not match the physical
        # state).
        best_pos = 0
        i = 0
        for pan_pos in scan_steps:
            if abs(pan_pos-position['x']) < abs(scan_steps[best_pos]
                                                - position['x']):
                best_pos = i
            i += 1
        current_scan_step = best_pos

    current_scan_step += 1
    p = helper.map(scan_steps[current_scan_step], -90, 90,
                   SERVO_MIN, SERVO_MAX)

    if position['x'] != p:
        # set_servo_pulse(PAN_PIN, p)
        print("set_servo_pulse {}", p)
        position['x'] = p

    scan_dirty = False


if __name__ == "__main__":
    """
    Test the servos.

    Usage: servos.py [<pin#> <angle_degrees>]
    """
    position = {
        'x': 0,
        'y': 0
    }

    set_servo_pulse(PAN_PIN, 0)
    set_servo_pulse(TILT_PIN, 0)

    while(True):
        scan()
