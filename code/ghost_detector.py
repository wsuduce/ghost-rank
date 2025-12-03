"""
Ghost Detector
==============

Batch processing tool for detecting Ghost curves in elliptic curve datasets.

Usage:
    python ghost_detector.py --input data.csv --output ghosts.csv
"""

import argparse
import csv
import math
from typing import List, Dict, Any
from stability_metric import compute_stability, classify_ghost, GHOST_THRESHOLD


def load_curves(filepath: str) -> List[Dict[str, Any]]:
    """
    Load elliptic curve data from CSV.
    
    Expected columns: label, conductor, rank, sha (optional), 
                      L_value (optional), L_prime (optional)
    """
    curves = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curves.append({
                'label': row.get('lmfdb_label', row.get('label', '')),
                'conductor': int(row.get('conductor', 0)),
                'rank': int(row.get('rank', 0)),
                'sha': float(row.get('sha', 1)),
                'L_value': float(row.get('L_value', 1)),
                'L_prime': float(row.get('L_prime', 0.1)),
            })
    return curves


def detect_ghosts(curves: List[Dict], rank_filter: int = 0) -> List[Dict]:
    """
    Detect Ghost curves in a dataset.
    
    Parameters
    ----------
    curves : List[Dict]
        List of curve data dictionaries
    rank_filter : int
        Only process curves with this rank (default: 0)
        
    Returns
    -------
    List[Dict]
        Curves classified as Ghosts with analysis data
    """
    ghosts = []
    
    for curve in curves:
        if curve['rank'] != rank_filter:
            continue
            
        if curve['conductor'] <= 1:
            continue
            
        stability = compute_stability(
            L_prime=curve['L_prime'],
            L_value=curve['L_value'],
            conductor=curve['conductor']
        )
        
        if classify_ghost(stability):
            ghosts.append({
                **curve,
                'stability': stability,
                'diffusion': -math.log10(stability) if stability > 0 else float('inf')
            })
    
    # Sort by Sha (largest first)
    ghosts.sort(key=lambda x: x['sha'], reverse=True)
    
    return ghosts


def compute_statistics(curves: List[Dict], ghosts: List[Dict]) -> Dict:
    """
    Compute detection statistics.
    """
    rank0_curves = [c for c in curves if c['rank'] == 0 and c['conductor'] > 1]
    
    # Contingency table
    ghosts_sha_gt_1 = sum(1 for g in ghosts if g['sha'] > 1)
    ghosts_sha_eq_1 = sum(1 for g in ghosts if g['sha'] == 1)
    
    total_sha_gt_1 = sum(1 for c in rank0_curves if c['sha'] > 1)
    total_sha_eq_1 = sum(1 for c in rank0_curves if c['sha'] == 1)
    
    # Ghost rates
    p_ghost_given_sha_gt_1 = ghosts_sha_gt_1 / total_sha_gt_1 if total_sha_gt_1 > 0 else 0
    p_ghost_given_sha_eq_1 = ghosts_sha_eq_1 / total_sha_eq_1 if total_sha_eq_1 > 0 else 0
    
    return {
        'total_curves': len(curves),
        'rank0_curves': len(rank0_curves),
        'ghosts_detected': len(ghosts),
        'ghosts_sha_gt_1': ghosts_sha_gt_1,
        'ghosts_sha_eq_1': ghosts_sha_eq_1,
        'p_ghost_given_sha_gt_1': p_ghost_given_sha_gt_1,
        'p_ghost_given_sha_eq_1': p_ghost_given_sha_eq_1,
        'perfect_separation': ghosts_sha_eq_1 == 0,
    }


def save_ghosts(ghosts: List[Dict], filepath: str):
    """Save ghost list to CSV."""
    if not ghosts:
        print("No ghosts to save.")
        return
        
    fieldnames = ['label', 'conductor', 'sha', 'stability', 'diffusion']
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(ghosts)
    
    print(f"Saved {len(ghosts)} ghosts to {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Detect Ghost curves in dataset')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file')
    parser.add_argument('--output', '-o', default='ghosts.csv', help='Output CSV file')
    parser.add_argument('--top', '-n', type=int, default=50, help='Show top N ghosts')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GHOST RANK DETECTOR")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading: {args.input}")
    curves = load_curves(args.input)
    print(f"Loaded: {len(curves):,} curves")
    
    # Detect ghosts
    print(f"\nScanning for Ghosts (threshold S < {GHOST_THRESHOLD})...")
    ghosts = detect_ghosts(curves)
    
    # Statistics
    stats = compute_statistics(curves, ghosts)
    
    print("\n" + "-" * 60)
    print("DETECTION STATISTICS")
    print("-" * 60)
    print(f"Total curves scanned: {stats['total_curves']:,}")
    print(f"Rank 0 curves: {stats['rank0_curves']:,}")
    print(f"Ghosts detected: {stats['ghosts_detected']:,}")
    print(f"\nP(Ghost | |Ш| > 1): {stats['p_ghost_given_sha_gt_1']:.2%}")
    print(f"P(Ghost | |Ш| = 1): {stats['p_ghost_given_sha_eq_1']:.2%}")
    print(f"\n✓ Perfect separation: {stats['perfect_separation']}")
    
    # Top ghosts
    print("\n" + "-" * 60)
    print(f"TOP {args.top} GHOSTS (by |Ш|)")
    print("-" * 60)
    print(f"{'Label':<20} {'Conductor':<12} {'|Ш|':<10} {'√|Ш|':<8} {'S':<12}")
    print("-" * 60)
    
    for g in ghosts[:args.top]:
        sqrt_sha = int(math.sqrt(g['sha']))
        perfect = '✓' if sqrt_sha * sqrt_sha == int(g['sha']) else ''
        print(f"{g['label']:<20} {g['conductor']:<12} {g['sha']:<10.0f} {sqrt_sha}{perfect:<6} {g['stability']:<12.6f}")
    
    # Save results
    save_ghosts(ghosts, args.output)
    
    print("\n" + "=" * 60)
    print("DETECTION COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()


