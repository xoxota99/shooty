import Adafruit_PCA9685
import logging
from config import cfg

logger = logging.getLogger(__name__)

# Set frequency to 50hz, good for servos.
PWM_FREQ = cfg.getint("pwm", "PWM_FREQ")

# Initialise the PCA9685 using the default address (0x40).
hat = Adafruit_PCA9685.PCA9685()
hat.set_pwm_freq(PWM_FREQ)
