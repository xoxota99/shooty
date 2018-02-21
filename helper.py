import math


def map(x, in_min, in_max, out_min, out_max):
    return ((x - in_min) * (out_max - out_min + 1)
            / (in_max - in_min + 1) + out_min)


def generateCurve(min_value, max_value, step_size_limit):
    """
    Generate a sine curve from the "from" value to the "to" value, not to
    exceed the given step size. Purpose of this is to have servos moving
    with relatively high rotating mass, without knocking over or de-calibrating
    the rig due to torque.
    """

    steps = (max_value-min_value) / step_size_limit
    retval = []

    half_range = (max_value - min_value)/2
    for i in range(1, steps):
        val = int(min_value + half_range + math.sin(math.pi*i/(steps/2))
                  * half_range)

        retval.append(val)

    return retval


if __name__ == "__main__":
    val = generateCurve(-99, 99, 2)
    print(val)
