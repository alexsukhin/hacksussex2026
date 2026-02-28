def evaluate_irrigation(moisture, ideal_min):
    if moisture < ideal_min:
        return "dry"
    else:
        return "optimal"