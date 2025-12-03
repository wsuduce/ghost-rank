# Reproducibility Guide

This document explains how to reproduce all results in the Ghost Rank paper.

---

## 1. Data Sources

### LMFDB (Primary Source)
- **URL:** https://www.lmfdb.org/EllipticCurve/Q/
- **Snapshot Date:** December 2024
- **Conductor Range Used:** 1,000 ≤ N ≤ 500,000

**To download:**
1. Go to LMFDB → Elliptic Curves → Search
2. Set conductor range
3. Select columns: `lmfdb_label`, `conductor`, `rank`, `sha`, `torsion`
4. Download as CSV

### Cremona Tables (Cross-validation)
- **URL:** https://johncremona.github.io/ecdata/
- **Used for:** Verifying |Ш| values

---

## 2. Core Algorithm

The stability metric is defined as:

```python
def compute_stability(L_prime, L_value, conductor):
    """
    Compute the Ghost Rank stability metric.
    
    Parameters:
        L_prime: |L'(E,1)| - first derivative at s=1
        L_value: |L(E,1)| - value at s=1
        conductor: N_E - conductor of the curve
    
    Returns:
        S(E) = |L'(E,1)| / (|L(E,1)| × log(N_E))
    """
    import math
    if L_value == 0 or conductor <= 1:
        return float('inf')
    return abs(L_prime) / (abs(L_value) * math.log(conductor))
```

### Ghost Classification

```python
def classify_ghost(stability, threshold=0.025):
    """
    Classify a curve as Ghost or Standard.
    
    Ghost curves have S < threshold and correlate with |Ш| > 1.
    """
    return stability < threshold
```

---

## 3. Reproducing Key Results

### Result 1: Perfect Separation (χ² = 95,060)

```python
# Load your LMFDB data
import pandas as pd
df = pd.read_csv('your_lmfdb_data.csv')

# Compute stability for rank 0 curves
rank0 = df[df['rank'] == 0]
rank0['stability'] = rank0.apply(
    lambda r: compute_stability(r['L_prime'], r['L_value'], r['conductor']),
    axis=1
)

# Classify
rank0['is_ghost'] = rank0['stability'] < 0.025

# Compute contingency table
ghosts_sha_gt_1 = ((rank0['is_ghost']) & (rank0['sha'] > 1)).sum()
ghosts_sha_eq_1 = ((rank0['is_ghost']) & (rank0['sha'] == 1)).sum()
standard_sha_gt_1 = ((~rank0['is_ghost']) & (rank0['sha'] > 1)).sum()
standard_sha_eq_1 = ((~rank0['is_ghost']) & (rank0['sha'] == 1)).sum()

print(f"Ghosts with |Ш|>1: {ghosts_sha_gt_1}")
print(f"Ghosts with |Ш|=1: {ghosts_sha_eq_1}")  # Should be 0!
```

### Result 2: Diffusion Law (slope = 1/√e)

```python
import numpy as np
from scipy import stats

# For curves with |Ш| ≥ 289
monsters = df[df['sha'] >= 289]
monsters['D'] = -np.log10(monsters['stability'])
monsters['log_sha'] = np.log10(monsters['sha'])

# Linear regression
slope, intercept, r, p, se = stats.linregress(
    monsters['log_sha'], 
    monsters['D']
)

print(f"Slope: {slope:.4f}")
print(f"Expected (1/√e): {1/np.sqrt(np.e):.4f}")
print(f"R²: {r**2:.4f}")
```

### Result 3: The Four Monsters

| Curve | Conductor | |Ш| | How to verify |
|-------|-----------|-----|---------------|
| 165066.v1 | 165,066 | 5625 | `EllipticCurve('165066v1').sha().an()` |
| 287175.n1 | 287,175 | 2500 | `EllipticCurve('287175n1').sha().an()` |
| 146850.cb1 | 146,850 | 2209 | `EllipticCurve('146850cb1').sha().an()` |
| 95438.c2 | 95,438 | 676 | `EllipticCurve('95438c2').sha().an()` |

**In SageMath:**
```python
E = EllipticCurve('165066v1')
print(f"Conductor: {E.conductor()}")
print(f"|Ш|: {E.sha().an()}")
```

---

## 4. Figure Reproduction

```bash
python code/generate_figures.py
```

This generates:
- `fig1_calibration_curve.png` — Diffusion law fit
- `fig2_monster_parade.png` — The four monsters
- `fig3_d3_anomaly.png` — The d3 anomaly

---

## 5. Computational Requirements

| Task | Time | Hardware |
|------|------|----------|
| Ghost detection (1M curves) | ~2 seconds | Any modern CPU |
| Calibration curve | ~1 second | Any modern CPU |
| |Ш| computation (traditional) | 48+ hours | HPC/CoCalc |

---

## 6. Known Limitations

1. **L-function data:** The stability metric requires L(E,1) and L'(E,1), which LMFDB provides pre-computed. Computing these yourself requires SageMath.

2. **Conductor range:** Our validation covers N < 500,000. Behavior at higher conductors may differ.

3. **d3 twist computation:** The |Ш| = 1225 for the d3 twist at conductor 5,282,112 was a single 48-hour computation. Independent verification is welcome.

---

## 7. Contact

For questions about reproducibility:
- Open a GitHub issue
- Email: adam@impactme.ai

---

*Last updated: December 2025*


