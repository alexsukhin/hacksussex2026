def evaluate_irrigation(current_moisture: int, ideal_moisture: int):
    """
    Calculates the watering score and returns the visual status indicator.
    """
    # Prevent division by zero just in case
    if ideal_moisture == 0:
        return {"score": 0, "status": "Dry", "color": "red"}

    # Calculate percentage score based on MVP formula
    score = int((current_moisture / ideal_moisture) * 100)

    # Determine status based on MVP thresholds
    if score < 80:
        return {"score": score, "status": "Dry", "color": "red"}
    elif score > 120:
        return {"score": score, "status": "Oversaturated", "color": "blue"}
    else:
        return {"score": score, "status": "Optimal", "color": "green"}