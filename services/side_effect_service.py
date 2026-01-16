import pickle
import os

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute path to data file
SIDE_EFFECT_PATH = os.path.join(BASE_DIR, "data", "side_effect_dict.pkl")

# Load side effect dictionary safely
with open(SIDE_EFFECT_PATH, "rb") as f:
    SIDE_EFFECTS = pickle.load(f)

def get_side_effects(drug1, drug2, limit=5):
    key = tuple(sorted([drug1, drug2]))

    if key not in SIDE_EFFECTS:
        return []

    effects = SIDE_EFFECTS[key].get("side_effects", [])
    severities = SIDE_EFFECTS[key].get("severity", [])

    result = []
    for i, effect in enumerate(effects[:limit]):
        sev = severities[i] if i < len(severities) else "moderate"
        result.append({
            "name": effect,
            "severity": sev
        })

    return result
