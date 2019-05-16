from __future__ import division
import math
import logging
# this only SEEMS to be unused, but some logging config is run on include.
import config

logger = logging.getLogger(__name__)


def map(x, in_min, in_max, out_min, out_max):
    """ 
    Maps values in one range to a value in another range. 
    See https://www.arduino.cc/reference/en/language/functions/math/map/ 
    """
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def generateCurve(min_value, max_value, step_size_limit):
    """
    Generate a sine curve from the "from" value to the "to" value, not to
    exceed the given step size. Purpose of this is to have servos moving
    with relatively high rotating mass, without knocking over or de-calibrating
    the rig due to torque.
    """

    steps = int((max_value-min_value) / step_size_limit)
    retval = []

    half_range = (max_value - min_value)/2
    for i in range(1, steps):
        val = int(min_value + half_range + math.sin(math.pi*i/(steps/2))
                  * half_range)

        retval.append(val)

    return retval


if __name__ == "__main__":
    val = generateCurve(-99, 99, 2)
    logger.info(val)
