def explain_side_effect(effect, severity):
    explanations = {
        "mild": f"{effect} is usually mild and may go away on its own.",
        "moderate": f"{effect} may cause discomfort and should be monitored.",
        "severe": f"{effect} can be serious. Seek medical help if it occurs."
    }
    return explanations.get(severity, f"{effect} may affect some people.")
