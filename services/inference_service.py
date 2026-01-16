import os
import torch
import pickle
from itertools import combinations

# --------------------------------------------------
# PyTorch Geometric safe loading (PyTorch 2.x)
# --------------------------------------------------
from torch.serialization import add_safe_globals
from torch_geometric.data.data import Data
from torch_geometric.data.storage import BaseStorage

add_safe_globals({
    Data: Data,
    BaseStorage: BaseStorage
})

# --------------------------------------------------
# PATH SETUP (MATCHES YOUR FOLDERS)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")

STATE_DICT_PATH = os.path.join(MODEL_DIR, "ddi_gnn_model.pth")
GRAPH_PATH = os.path.join(DATA_DIR, "ddi_graph_data.pt")
MAP_PATH = os.path.join(DATA_DIR, "drug_index_mapping.pkl")

# --------------------------------------------------
# LOAD GRAPH DATA (IMPORTANT FIX)
# --------------------------------------------------
graph_data = torch.load(
    GRAPH_PATH,
    map_location="cpu",
    weights_only=False
)

# --------------------------------------------------
# LOAD DRUG INDEX MAPPING
# --------------------------------------------------
with open(MAP_PATH, "rb") as f:
    mapping = pickle.load(f)

drug_to_idx = mapping["drug_to_idx"]

# --------------------------------------------------
# LOAD MODEL ARCHITECTURE (EXACT MATCH)
# --------------------------------------------------
from model.ddi_gnn_model import DDIGNN

device = torch.device("cpu")

# Your model expects: in_channels, hidden_channels
in_channels = graph_data.x.shape[1]
hidden_channels = 64 # ⚠️ MUST MATCH TRAINING VALUE

model = DDIGNN(
    in_channels=in_channels,
    hidden_channels=hidden_channels
)

# --------------------------------------------------
# LOAD TRAINED WEIGHTS
# --------------------------------------------------
state_dict = torch.load(STATE_DICT_PATH, map_location=device)
model.load_state_dict(state_dict)
model.to(device)
model.eval()

# --------------------------------------------------
# PREDICTION FUNCTION (PAIRWISE POLYPHARMACY)
# --------------------------------------------------
def predict(drug_ids):
    """
    drug_ids: list of DrugBank IDs
    returns: list of {drug1, drug2, probability}
    """

    results = []

    for d1, d2 in combinations(drug_ids, 2):

        # Skip unknown drugs safely
        if d1 not in drug_to_idx or d2 not in drug_to_idx:
            continue

        i = drug_to_idx[d1]
        j = drug_to_idx[d2]

        with torch.no_grad():
            prob = model(
                graph_data.x,
                graph_data.edge_index,
                i,
                j
            )

            # prob is a tensor → convert to float
            prob = prob.item()

        results.append({
            "drug1": d1,
            "drug2": d2,
            "probability": float(prob)
        })

    return results
