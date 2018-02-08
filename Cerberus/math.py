
def map(x, in_min, in_max, out_min, out_max):
    return ((x - in_min) * (out_max - out_min + 1)
            / (in_max - in_min + 1) + out_min)
