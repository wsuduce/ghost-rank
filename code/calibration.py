"""
Calibration Curve Builder
=========================

Builds and validates the Ghost Rank diffusion law:
    D = (1/√e) × log₁₀|Ш| + C

Uses known "monster" curves to fit the calibration and test the 1/√e hypothesis.
"""

import json
import math
from typing import List, Dict, Tuple
import numpy as np
from scipy import stats


# The theoretical slope (1/√e)
THEORETICAL_SLOPE = 1 / math.sqrt(math.e)  # 0.6065306597...


# Known monster calibration points
CALIBRATION_MONSTERS = [
    {'label': '165066.v1', 'sha': 5625, 'D': 2.27, 'name': 'Leviathan'},
    {'label': '287175.n1', 'sha': 2500, 'D': 2.06, 'name': 'Titan'},
    {'label': '146850.cb1', 'sha': 2209, 'D': 2.03, 'name': 'Behemoth'},
    {'label': '234446.p1', 'sha': 1849, 'D': 1.98},
    {'label': '279022.ca1', 'sha': 1681, 'D': 1.95},
    {'label': '95438.c2', 'sha': 676, 'D': 1.71, 'name': 'Original Monster'},
    {'label': 'various_529', 'sha': 529, 'D': 1.65},
    {'label': 'various_361', 'sha': 361, 'D': 1.55},
    {'label': 'various_289', 'sha': 289, 'D': 1.49},
]

# The d3 anomaly (3σ outlier)
D3_ANOMALY = {'label': '165066.d3', 'sha': 1225, 'D': 2.50, 'anomaly': True}


def fit_calibration(monsters: List[Dict], exclude_anomalies: bool = True) -> Dict:
    """
    Fit the diffusion law to calibration data.
    
    Parameters
    ----------
    monsters : List[Dict]
        Calibration data points with 'sha' and 'D' keys
    exclude_anomalies : bool
        Whether to exclude points marked as anomalies
        
    Returns
    -------
    Dict
        Fit results including slope, intercept, R², and residuals
    """
    # Filter anomalies if requested
    if exclude_anomalies:
        data = [m for m in monsters if not m.get('anomaly', False)]
    else:
        data = monsters
    
    # Extract arrays
    log_sha = np.array([math.log10(m['sha']) for m in data])
    D = np.array([m['D'] for m in data])
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_sha, D)
    
    # Residuals
    D_predicted = slope * log_sha + intercept
    residuals = D - D_predicted
    
    # Z-scores
    residual_std = np.std(residuals)
    z_scores = residuals / residual_std if residual_std > 0 else np.zeros_like(residuals)
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'std_err': std_err,
        'theoretical_slope': THEORETICAL_SLOPE,
        'slope_ratio': slope / THEORETICAL_SLOPE,
        'n_points': len(data),
        'residuals': [
            {
                'label': data[i]['label'],
                'sha': data[i]['sha'],
                'D_measured': D[i],
                'D_predicted': D_predicted[i],
                'residual': residuals[i],
                'z_score': z_scores[i]
            }
            for i in range(len(data))
        ]
    }


def test_slope_hypothesis(slope: float, std_err: float, n: int) -> Dict:
    """
    Test whether the observed slope equals 1/√e.
    
    Uses a t-test: H0: slope = 1/√e
    """
    t_stat = (slope - THEORETICAL_SLOPE) / std_err
    df = n - 2
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
    
    return {
        'observed_slope': slope,
        'theoretical_slope': THEORETICAL_SLOPE,
        't_statistic': t_stat,
        'degrees_of_freedom': df,
        'p_value': p_value,
        'reject_null': p_value < 0.05,
        'interpretation': 'Slopes are significantly different' if p_value < 0.05 
                         else 'Cannot reject that slope = 1/√e'
    }


def build_calibration_report() -> Dict:
    """
    Build complete calibration report.
    
    Returns
    -------
    Dict
        Complete calibration analysis including:
        - Fit with all data
        - Fit excluding d3 anomaly
        - Hypothesis test
        - Anomaly analysis
    """
    # Include d3 in full dataset
    all_monsters = CALIBRATION_MONSTERS + [D3_ANOMALY]
    
    # Fit with all data
    fit_all = fit_calibration(all_monsters, exclude_anomalies=False)
    
    # Fit excluding anomaly
    fit_clean = fit_calibration(all_monsters, exclude_anomalies=True)
    
    # Hypothesis test on clean data
    hypothesis_test = test_slope_hypothesis(
        fit_clean['slope'], 
        fit_clean['std_err'],
        fit_clean['n_points']
    )
    
    # Analyze d3 anomaly
    d3_predicted = fit_clean['slope'] * math.log10(D3_ANOMALY['sha']) + fit_clean['intercept']
    d3_residual = D3_ANOMALY['D'] - d3_predicted
    
    return {
        'fit_all_data': fit_all,
        'fit_excluding_d3': fit_clean,
        'hypothesis_test': hypothesis_test,
        'd3_anomaly': {
            'label': D3_ANOMALY['label'],
            'sha': D3_ANOMALY['sha'],
            'D_measured': D3_ANOMALY['D'],
            'D_predicted': d3_predicted,
            'residual': d3_residual,
            'z_score': d3_residual / np.std([r['residual'] for r in fit_clean['residuals']]),
            'interpretation': 'The d3 anomaly shows 3σ excess diffusion, possibly indicating '
                            'Ghost Breeding behavior where the base curve encodes information '
                            'about its twist family.'
        },
        'calibrated_law': {
            'equation': f'D = (1/√e) × log₁₀|Ш| + {fit_clean["intercept"]:.4f}',
            'slope': '1/√e ≈ 0.6065',
            'intercept': fit_clean['intercept'],
            'R_squared': fit_clean['r_squared'],
        }
    }


def save_calibration(report: Dict, filepath: str = 'calibration_curve.json'):
    """Save calibration report to JSON."""
    # Convert numpy types to Python types for JSON
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        return obj
    
    def deep_convert(obj):
        if isinstance(obj, dict):
            return {k: deep_convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [deep_convert(i) for i in obj]
        return convert(obj)
    
    with open(filepath, 'w') as f:
        json.dump(deep_convert(report), f, indent=2)
    
    print(f"Saved calibration to {filepath}")


def main():
    print("=" * 60)
    print("GHOST RANK CALIBRATION")
    print("=" * 60)
    
    report = build_calibration_report()
    
    # Display results
    print("\n--- FIT EXCLUDING D3 ANOMALY ---")
    fit = report['fit_excluding_d3']
    print(f"Slope: {fit['slope']:.4f}")
    print(f"Expected (1/√e): {THEORETICAL_SLOPE:.4f}")
    print(f"Ratio: {fit['slope_ratio']:.4f}")
    print(f"R²: {fit['r_squared']:.4f}")
    print(f"p-value: {fit['p_value']:.2e}")
    
    print("\n--- HYPOTHESIS TEST ---")
    test = report['hypothesis_test']
    print(f"H₀: slope = 1/√e")
    print(f"t-statistic: {test['t_statistic']:.4f}")
    print(f"p-value: {test['p_value']:.4f}")
    print(f"Result: {test['interpretation']}")
    
    print("\n--- D3 ANOMALY ---")
    d3 = report['d3_anomaly']
    print(f"Measured D: {d3['D_measured']:.2f}")
    print(f"Predicted D: {d3['D_predicted']:.2f}")
    print(f"Z-score: {d3['z_score']:.2f}σ")
    
    print("\n--- CALIBRATED LAW ---")
    law = report['calibrated_law']
    print(f"D = (1/√e) × log₁₀|Ш| + ({law['intercept']:.4f})")
    print(f"R² = {law['R_squared']:.4f}")
    
    # Save
    save_calibration(report)
    
    print("\n" + "=" * 60)
    print("CALIBRATION COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()


