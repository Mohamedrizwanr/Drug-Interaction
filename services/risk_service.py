def risk(probability):
    """
    Convert probability (0–1) into risk score and severity.
    """

    score = int(probability * 100)

    if score < 30:
        return score, "MILD"
    elif score < 60:
        return score, "MODERATE"
    else:
        return score, "SEVERE"
