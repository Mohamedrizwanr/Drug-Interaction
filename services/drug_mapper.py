import pandas as pd
import os

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute path to CSV
CSV_PATH = os.path.join(BASE_DIR, "data", "cleaned_drugs.csv")

# Load CSV
df = pd.read_csv(CSV_PATH)

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# Use correct column names
df["drug_name"] = df["drug_name"].astype(str).str.lower()

# Build mapping: drug name → DrugBank ID
MAP = dict(zip(df["drug_name"], df["drugbank_id"]))


def get_id(name):
    """
    Convert medicine name to DrugBank ID.
    Returns None if medicine is unknown.
    """
    if not name:
        return None
    return MAP.get(name.lower())


def autocomplete(prefix, limit=8):
    """
    Autocomplete suggestions for UI.
    Starts from 2nd letter (handled in frontend).
    """
    prefix = prefix.lower()
    return [k for k in MAP.keys() if k.startswith(prefix)][:limit]
