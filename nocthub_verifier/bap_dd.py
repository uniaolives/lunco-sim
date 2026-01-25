"""
Byzantine Agreement Protocol with Drift Detection (BAP-DD) v1.1 - Prototype
Implements EWMC (Exponentially Weighted Moving Consensus) and mock HLC (Hybrid Logical Clock).
"""

import math
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class HLC:
    """Mock Hybrid Logical Clock"""
    pt: int  # Physical Time
    l:  int  # Logical Counter
    c:  int  # Causal ID (Node ID)

    def __lt__(self, other):
        if self.l != other.l:
            return self.l < other.l
        if self.c != other.c:
            return self.c < other.c
        return self.pt < other.pt

class BAPDD:
    def __init__(self, num_granules: int = 4, alpha: float = 0.95, beta: float = 10.0):
        self.num_granules = num_granules
        self.alpha = alpha
        self.beta = beta
        # Drift vectors D_ij for all i, j
        self.drift_vectors = [[0.0 for _ in range(num_granules)] for _ in range(num_granules)]
        # Weights for each granule
        self.weights = [1.0 for _ in range(num_granules)]
        # Priority Map for Partition Priest Protocol
        self.priority_map = {0: 1, 1: 2, 2: 3, 3: 4} # Node: Priority (Lower is higher)

    def update_drift(self, opinions: List[float], hlcs: List[HLC]):
        """Updates drift vectors based on current opinions and HLCs."""
        for i in range(self.num_granules):
            for j in range(self.num_granules):
                # Class C detection: opinion divergence
                diff = abs(opinions[i] - opinions[j])

                # HLC divergence check (Simplified)
                # If logical clocks diverge significantly, increase perceived drift
                causal_diff = abs(hlcs[i].l - hlcs[j].l)
                drift_contribution = diff * (1 + 0.1 * causal_diff)

                self.drift_vectors[i][j] = (self.alpha * self.drift_vectors[i][j] +
                                            (1 - self.alpha) * drift_contribution)

        self._update_weights()

    def _update_weights(self):
        """Recalculates authority weights based on accumulated drift."""
        for j in range(self.num_granules):
            sum_drift = sum(self.drift_vectors[i][j] for i in range(self.num_granules) if i != j)
            self.weights[j] = 1.0 / (1.0 + self.beta * sum_drift)

    def resolve_partition(self, subgroups: List[List[int]]) -> int:
        """Partition Priest Protocol: Returns the index of the winning Priest node."""
        priest_candidates = []
        for group in subgroups:
            # Find the highest priority node in each group
            group_leader = min(group, key=lambda node: self.priority_map[node])
            priest_candidates.append(group_leader)

        # Global winner is the one with highest priority among group leaders
        winning_priest = min(priest_candidates, key=lambda node: self.priority_map[node])
        return winning_priest

    def get_consensus_opinion(self, opinions: List[float]) -> float:
        """Calculates the weighted consensus opinion."""
        total_weight = sum(self.weights)
        if total_weight == 0: return sum(opinions) / len(opinions)

        weighted_sum = sum(o * w for o, w in zip(opinions, self.weights))
        return weighted_sum / total_weight

def main():
    bap = BAPDD(num_granules=4)
    hlcs = [HLC(int(time.time()), 0, i) for i in range(4)]

    print("--- Simulation 1: Class C Silent Drift Detection ---")
    for t in range(50):
        # Granule 1 (Beta) has a 10% bias
        opinions = [70.0, 77.0, 70.0, 70.0]
        # Increment logical clocks
        for h in hlcs: h.l += 1

        bap.update_drift(opinions, hlcs)
        if t % 10 == 0:
            print(f"Round {t}: Weights = {[round(w, 3) for w in bap.weights]}")

    print("\n--- Simulation 2: Partition Priest Resolution ---")
    # Scenario: [0, 1] vs [2, 3]
    subgroups = [[0, 1], [2, 3]]
    winner = bap.resolve_partition(subgroups)
    print(f"Subgroups: {subgroups}")
    print(f"Winning Priest (Node with highest priority): Granule {winner} (Priority {bap.priority_map[winner]})")

if __name__ == "__main__":
    main()
