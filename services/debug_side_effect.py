import pickle
import os

# =====================================================
# PROJECT ROOT
# services/side_effect_service.py → go up two levels
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "side_effect_dict.pkl")

# =====================================================
# LOAD SIDE EFFECT DICTIONARY
# =====================================================
with open(DATA_PATH, "rb") as f:
    SIDE_EFFECTS = pickle.load(f)


def get_side_effects(drug1, drug2, limit=5):
    """
    Returns side effects for a drug pair.
    Handles order + structure safely.
    """

    # DrugBank pairs can be stored in any order
    key1 = (drug1, drug2)
    key2 = (drug2, drug1)

    record = None

    if key1 in SIDE_EFFECTS:
        record = SIDE_EFFECTS[key1]
    elif key2 in SIDE_EFFECTS:
        record = SIDE_EFFECTS[key2]
    else:
        return []

    effects = []
    severities = []

    # Handle expected dict format
    if isinstance(record, dict):
        effects = record.get("side_effects", [])
        severities = record.get("severity", [])

    # Handle list-only format (fallback)
    elif isinstance(record, list):
        effects = record
        severities = ["moderate"] * len(effects)

    results = []
    for i, effect in enumerate(effects[:limit]):
        sev = severities[i] if i < len(severities) else "moderate"
        results.append({
            "name": effect,
            "severity": sev.lower()
        })

    return results
if __name__ == "__main__":
    print("Loaded side effect pairs:", len(SIDE_EFFECTS))
