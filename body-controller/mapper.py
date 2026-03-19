def map_range(value, in_min, in_max, out_min, out_max):
    #mapping function
    mapped = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return int(max(out_min, min(out_max, mapped)))
