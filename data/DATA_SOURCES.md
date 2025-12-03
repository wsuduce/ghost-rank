# Data Sources

This document describes how to obtain the raw data needed to reproduce Ghost Rank experiments.

---

## Primary Source: LMFDB

**URL:** https://www.lmfdb.org/EllipticCurve/Q/

### How to Download

1. Go to LMFDB → Elliptic Curves over ℚ → Search
2. Set your conductor range (e.g., 1000 to 100000)
3. Add columns: `lmfdb_label`, `conductor`, `rank`, `sha`, `torsion`
4. Click "Download" → CSV

### Recommended Ranges

| Band | Conductor Range | Approx. Curves |
|------|-----------------|----------------|
| 1 | 1,000 - 10,000 | ~60,000 |
| 2 | 10,000 - 100,000 | ~650,000 |
| 3 | 100,000 - 200,000 | ~350,000 |
| 4 | 200,000 - 500,000 | ~600,000 |

---

## Secondary Source: Cremona Tables

**URL:** https://johncremona.github.io/ecdata/

The Cremona tables provide cross-validation for |Ш| values.

### Files of Interest

- `allbsd.NNNNN-MMMMM.gz` — BSD data including |Ш|
- `allgens.NNNNN-MMMMM.gz` — Generators and torsion

---

## Data We Provide

Due to size constraints, we include only:

1. **`monsters.json`** — The four main monster curves with full details
2. **`calibration_curve.json`** — Calibration fit results

For full reproducibility, download the LMFDB data as described above.

---

## Verification Commands (SageMath)

To verify individual curves:

```python
# In SageMath
E = EllipticCurve('165066v1')
print(f"Conductor: {E.conductor()}")
print(f"|Ш|: {E.sha().an()}")
print(f"Rank: {E.rank()}")
print(f"Torsion: {E.torsion_order()}")
```

---

## Data Format

Expected CSV columns:

| Column | Type | Description |
|--------|------|-------------|
| `lmfdb_label` | string | e.g., "165066.v1" |
| `conductor` | int | N_E |
| `rank` | int | Analytic rank (0 or 1) |
| `sha` | float | |Ш|_an (analytic) |
| `torsion` | int | Torsion order |

---

## License

LMFDB data is available under Creative Commons CC-BY-SA 4.0.


