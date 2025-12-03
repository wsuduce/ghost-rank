"""
Ghost Rank Stability Metric
===========================

Core algorithm for computing the Ghost Rank stability metric on elliptic curves.

The stability metric S(E) detects curves with large Tate-Shafarevich groups (|Ш|)
by analyzing the behavior of L-functions at s=1.

Reference: Murphy (2025), "Ghost Rank: Spectral Phase Transitions and the 
           1/√e Diffusion Law in Elliptic Curves"
"""

import math
from typing import Tuple, Optional

# Ghost threshold - curves below this are likely to have |Ш| > 1
GHOST_THRESHOLD = 0.025

# The universal diffusion constant (1/√e)
DIFFUSION_SLOPE = 1 / math.sqrt(math.e)  # ≈ 0.6065


def compute_stability(L_prime: float, L_value: float, conductor: int) -> float:
    """
    Compute the Ghost Rank stability metric S(E).
    
    Parameters
    ----------
    L_prime : float
        The absolute value of L'(E, 1) - the first derivative at s=1
    L_value : float
        The absolute value of L(E, 1) - the L-function value at s=1
    conductor : int
        The conductor N_E of the elliptic curve
        
    Returns
    -------
    float
        The stability metric S(E) = |L'(E,1)| / (|L(E,1)| × log(N_E))
        
    Notes
    -----
    For rank 0 curves: Lower S indicates potential "Ghost" behavior
    For rank 1 curves: Use compute_stability_rank1() instead
    
    Examples
    --------
    >>> S = compute_stability(L_prime=0.5, L_value=2.0, conductor=165066)
    >>> print(f"Stability: {S:.6f}")
    """
    if L_value == 0:
        return float('inf')
    if conductor <= 1:
        raise ValueError("Conductor must be > 1")
    
    return abs(L_prime) / (abs(L_value) * math.log(conductor))


def compute_stability_rank1(L_double_prime: float, L_prime: float, 
                            conductor: int) -> float:
    """
    Compute stability metric for rank 1 curves.
    
    For rank 1 curves, L(E,1) = 0, so we use the next derivative.
    
    Parameters
    ----------
    L_double_prime : float
        The absolute value of L''(E, 1)
    L_prime : float
        The absolute value of L'(E, 1)
    conductor : int
        The conductor N_E
        
    Returns
    -------
    float
        The rank-1 stability metric S₁(E)
    """
    if L_prime == 0:
        return float('inf')
    if conductor <= 1:
        raise ValueError("Conductor must be > 1")
    
    return abs(L_double_prime) / (abs(L_prime) * math.log(conductor))


def compute_diffusion(stability: float, conductor: int) -> float:
    """
    Compute the diffusion index D from stability.
    
    Parameters
    ----------
    stability : float
        The stability metric S(E)
    conductor : int
        The conductor (used for normalization)
        
    Returns
    -------
    float
        The diffusion index D = -log₁₀(S) normalized by conductor
    """
    if stability <= 0:
        return float('inf')
    
    log_N = math.log10(conductor)
    return -math.log10(stability) / (log_N / 10)


def predict_sha(diffusion: float) -> float:
    """
    Predict |Ш| from diffusion using the calibrated law.
    
    Uses: D = (1/√e) × log₁₀|Ш| + C
    Inverted: |Ш| = 10^((D - C) × √e)
    
    Parameters
    ----------
    diffusion : float
        The diffusion index D
        
    Returns
    -------
    float
        Predicted |Ш| value
        
    Notes
    -----
    The calibration constant C ≈ -0.0025 from the paper.
    Predictions are typically accurate to within an order of magnitude.
    """
    C = -0.0025
    sqrt_e = math.sqrt(math.e)
    log_sha = (diffusion - C) / DIFFUSION_SLOPE
    return 10 ** log_sha


def classify_ghost(stability: float, threshold: float = GHOST_THRESHOLD) -> bool:
    """
    Classify a curve as Ghost or Standard.
    
    Parameters
    ----------
    stability : float
        The stability metric S(E)
    threshold : float, optional
        Classification threshold (default: 0.025)
        
    Returns
    -------
    bool
        True if the curve is classified as a Ghost
        
    Notes
    -----
    Ghost curves have |Ш| > 1 with 100% specificity in our dataset.
    """
    return stability < threshold


def analyze_curve(L_prime: float, L_value: float, conductor: int,
                  rank: int = 0) -> dict:
    """
    Full Ghost Rank analysis of an elliptic curve.
    
    Parameters
    ----------
    L_prime : float
        |L'(E, 1)|
    L_value : float
        |L(E, 1)|
    conductor : int
        The conductor N_E
    rank : int, optional
        Analytic rank (default: 0)
        
    Returns
    -------
    dict
        Complete analysis including:
        - stability: The S(E) metric
        - diffusion: The D index
        - is_ghost: Boolean classification
        - predicted_sha: Estimated |Ш|
        - confidence: Classification confidence level
    """
    if rank == 0:
        stability = compute_stability(L_prime, L_value, conductor)
    else:
        # For rank > 0, we'd need L''(E,1)
        raise NotImplementedError("Rank > 0 requires L''(E,1)")
    
    diffusion = compute_diffusion(stability, conductor)
    is_ghost = classify_ghost(stability)
    predicted_sha = predict_sha(diffusion) if is_ghost else 1.0
    
    # Confidence based on distance from threshold
    distance = abs(stability - GHOST_THRESHOLD) / GHOST_THRESHOLD
    confidence = min(1.0, distance)
    
    return {
        'stability': stability,
        'diffusion': diffusion,
        'is_ghost': is_ghost,
        'predicted_sha': predicted_sha,
        'confidence': confidence
    }


# Known monster curves for reference
MONSTERS = {
    '165066.v1': {'sha': 5625, 'sqrt_sha': 75, 'name': 'Leviathan'},
    '287175.n1': {'sha': 2500, 'sqrt_sha': 50, 'name': 'Titan'},
    '146850.cb1': {'sha': 2209, 'sqrt_sha': 47, 'name': 'Behemoth'},
    '95438.c2': {'sha': 676, 'sqrt_sha': 26, 'name': 'Original Monster'},
}


if __name__ == '__main__':
    # Example usage
    print("Ghost Rank Stability Metric")
    print("=" * 40)
    
    # Test with Leviathan-like values
    result = analyze_curve(
        L_prime=0.1,
        L_value=4.93,
        conductor=165066
    )
    
    print(f"Stability: {result['stability']:.6f}")
    print(f"Diffusion: {result['diffusion']:.4f}")
    print(f"Is Ghost: {result['is_ghost']}")
    print(f"Predicted |Ш|: {result['predicted_sha']:.0f}")
    print(f"Confidence: {result['confidence']:.2%}")


