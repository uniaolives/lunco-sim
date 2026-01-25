# Byzantine Agreement Protocol with Drift Detection (BAP-DD) v1.1

## I. Mathematical Foundation

**System Model:**
- $N = 4$ granules (Crew Modules A-D), tolerating $f = 1$ Byzantine fault (radiation-corrupted node)
- Each granule $i$ maintains local state $\theta_i \in \mathbb{R}^d$ (model parameters) and medical opinion $m_i \in \mathcal{M}$ (diagnosis/proposal)
- Communication graph: Fully connected with asynchronous message passing (20-40 min Mars delay)

**Threat Model (FIM Mapping):**
- **Class A (Confident Hallucinator)**: $m_i$ has entropy $H(m_i) \approx 0$ (false certainty) but $\theta_i$ diverges from consensus
- **Class B (Entropy Storm)**: $\text{Var}(H(m_i)) > \tau$ over time window $T$ (unstable confidence)
- **Class C (Silent Drift)**: $\|\theta_i(t) - \theta_i(t-\Delta t)\| < \epsilon$ locally but $\|m_i - \text{median}(m_{j \neq i})\| > \delta$ globally

## II. The Hybrid Logical Clock (HLC) Specification

**Objective:** Provide a causality-preserving time standard that tracks "happened-before" relationships even when physical clocks drift or jump due to radiation SEUs.

**Data Structure:**
We replace the standard `timestamp` with a 3-tuple `HLC`:

```rust
struct HLC {
    pt: u64, // Physical Time (NTP/Atomic Clock - max perceived system time)
    l:  u16, // Logical Counter (for events within the same physical tick)
    c:  u8,  // Causal ID (Node ID: Alpha=0, Beta=1, Gamma=2, Delta=3)
}
```

**Integration with BAP-DD:**
- **Drift Calculation:** Drift is no longer calculated by physical seconds, but by **HLC divergence**.
- **Temporal Authority:** The consensus weight $w_j^{temp}$ prioritizes the proposal with the **lowest HLC** (oldest valid causal origin), preventing a fast-drifting node from spamming the network with "newer" decisions.

## III. The Partition Priest Protocol (Deterministic Conflict Resolution)

**Objective:** Resolve "Split-Brain" forks deterministically without human intervention.

**The Static Hierarchy (The "Line of Succession"):**
1. **Granule α (Medical Officer Module):** Priority 1
2. **Granule β (Command Module):** Priority 2
3. **Granule γ (Habitation):** Priority 3
4. **Granule δ (Engineering):** Priority 4

**The "Reconciliation Handshake" Protocol:**
When the network partition heals, sub-groups exchange their canonical HLC history tips.
1. Compare priorities of the highest active node in each group.
2. The sub-group containing the highest-priority granule has its timeline adopted.
3. The losing sub-group initiates **State Rollback** and archives its decisions in a KARNAK "Shadow Block" (marked valid-but-overruled).

## IV. Drift Detection: Exponentially Weighted Moving Consensus (EWMC)

Each granule maintains a **consensus drift vector** for every other granule:

$$D_{ij}(t) = \alpha \cdot D_{ij}(t-1) + (1-\alpha) \cdot \|m_i(t) - m_j(t)\|_2$$

- **Alert Threshold**: If $D_{ij}(t) > 0.15$ for $t > 6$ hours, flag granule $j$ as "drifting".
- **Weighting Phase**: $w_j(t) = \frac{1}{1 + \beta \cdot \sum_{i \neq j} D_{ij}(t)}$.

## V. Consensus State Machine

- **Normal Operation**: Weighted median consensus achieved if $\sum w_j > 0.75$.
- **Judgment Hysteresis**: Triggered by $\sigma(H(m_j)) > \tau$; buffers proposals for 40 min.
- **Safe Mode**: Activated if deadlock persists; stabilizes patient and escalates to Earth.
- **Stochastic Resolution**: In life-threatening emergencies, select proposal with probability proportional to $w_j \cdot H(m_j)$.

## VI. Antarctic Validation
- **Week 6 Split-Fleet Scenario**: Physically partition the network, inject Class C drift into one node, and verify that the Partition Priest Protocol correctly selects the canonical timeline upon reconnection.
