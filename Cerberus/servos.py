from __future__ import division
import math
import time
import Adafruit_PCA9685

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
    p = math.map(pan, -90, 90, SERVO_MIN, SERVO_MAX)
    t = math.map(tilt, -90, 90, SERVO_MIN, SERVO_MAX)
    set_servo_pulse(PAN_PIN, p)
    set_servo_pulse(TILT_PIN, t)


if __name__ == "__main__":
    """
    Test the servos.

    Usage: servos.py [<pin#> <angle_degrees>]
    """
    import sys
    if(len(sys.argv) == 1):
        # no arguments.
        while True:
            # Move servo on channel O between extremes.
            set_servo_pulse(PAN_PIN, SERVO_MIN)
            set_servo_pulse(TILT_PIN, SERVO_MIN)
            time.sleep(1)
            set_servo_pulse(TILT_PIN, SERVO_MAX)
            time.sleep(1)
            set_servo_pulse(PAN_PIN, SERVO_MAX)
            time.sleep(1)
            set_servo_pulse(TILT_PIN, SERVO_MIN)
            time.sleep(1)
    elif(len(sys.argv) >= 3):
        srv_num = int(sys.argv[1])
        if(srv_num < 16):
            srv_angle = int(sys.argv[2])
            if(-90 <= srv_angle <= 90):
                set_servo_pulse(srv_num, map(srv_angle, -90, 90, SERVO_MIN,
                                             SERVO_MAX))
            else:
                print("Invalid argument <degrees>. Valid values are between -90 \
                and 90.")
        else:
            print("Invalid argument <pin#>. Valid values are between 0 and \
            15.")
    else:
        print("Usage: servos.py [<pin#> <angle_degrees>]")
