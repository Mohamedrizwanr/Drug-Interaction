import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

class DDIGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.lin = nn.Linear(hidden_channels * 2, 1)   # ✅ MATCHES TRAINING

    def forward(self, x, edge_index, i, j):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)

        h_i = x[i]
        h_j = x[j]
        h = torch.cat([h_i, h_j], dim=-1)

        return torch.sigmoid(self.lin(h))   # ✅ MATCHES TRAINING
