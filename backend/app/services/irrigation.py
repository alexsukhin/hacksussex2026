def evaluate_irrigation(moisture, ideal_min, ideal_max):
    if moisture < ideal_min:
        return "dry"
    elif moisture > ideal_max:
        return "oversaturated"
    else:
        return "optimal"