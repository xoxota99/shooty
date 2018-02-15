import math


def map(x, in_min, in_max, out_min, out_max):
    return ((x - in_min) * (out_max - out_min + 1)
            / (in_max - in_min + 1) + out_min)


def generateCurve(start, end, step_size_limit):
    """
    Generate a sine curve from the "from" value to the "to" value, not to
    exceed the given step size. Purpose of this is to have servos moving
    with relatively high rotating mass, without knocking over or de-calibrating
    the rig due to torque.
    """

    step_count = (end-start) / step_size_limit
    steps = []
    halfRange = (end - start) / 2
    i = 0
    while(i < step_count):
        n = end - (halfRange + math.cos(math.pi * i / step_count) * halfRange)
        i += 1
        steps.append(n)

    return steps
