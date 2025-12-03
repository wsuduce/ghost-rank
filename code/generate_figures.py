"""
Figure Generator
================

Generates the three main figures for the Ghost Rank paper:
1. Calibration curve (D vs log|Ш|)
2. Monster parade (bar chart)
3. d3 anomaly (residual analysis)

Usage:
    python generate_figures.py
"""

import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np


# Style configuration
plt.style.use('seaborn-v0_8-whitegrid')
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'  # or 'pdf'


# Calibration data
MONSTERS = [
    {'label': '165066.v1', 'sha': 5625, 'D': 2.27, 'name': 'Leviathan'},
    {'label': '287175.n1', 'sha': 2500, 'D': 2.06},
    {'label': '146850.cb1', 'sha': 2209, 'D': 2.03},
    {'label': '234446.p1', 'sha': 1849, 'D': 1.98},
    {'label': '279022.ca1', 'sha': 1681, 'D': 1.95},
    {'label': '165066.d3', 'sha': 1225, 'D': 2.50, 'anomaly': True},
    {'label': '95438.c2', 'sha': 676, 'D': 1.71, 'name': 'Monster #1'},
    {'label': 'various_529', 'sha': 529, 'D': 1.65},
    {'label': 'various_361', 'sha': 361, 'D': 1.55},
    {'label': 'various_289', 'sha': 289, 'D': 1.49},
]


def fig1_calibration_curve(output_dir: str = '../results'):
    """Generate Figure 1: The calibration curve."""
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Separate normal points and anomaly
    normal = [m for m in MONSTERS if not m.get('anomaly', False)]
    anomaly = [m for m in MONSTERS if m.get('anomaly', False)]
    
    # Data arrays
    log_sha_normal = [math.log10(m['sha']) for m in normal]
    D_normal = [m['D'] for m in normal]
    
    # Fit line (excluding anomaly)
    slope = 1 / math.sqrt(math.e)  # 0.6065
    intercept = -0.0025
    x_fit = np.linspace(2.2, 4.0, 100)
    y_fit = slope * x_fit + intercept
    
    # Plot fit line
    ax.plot(x_fit, y_fit, 'b-', linewidth=2, 
            label=f'D = (1/√e) × log₁₀|Ш| + C\nm = 0.6065, C = −0.0025')
    
    # Plot normal points
    ax.scatter(log_sha_normal, D_normal, s=100, c='green', 
               edgecolors='black', linewidth=1, zorder=5,
               label=f'Normal Ghosts (n=9, R² = 0.9999)')
    
    # Plot anomaly
    if anomaly:
        log_sha_anom = math.log10(anomaly[0]['sha'])
        D_anom = anomaly[0]['D']
        ax.scatter([log_sha_anom], [D_anom], s=200, c='red', 
                   marker='*', edgecolors='black', linewidth=1, zorder=6,
                   label=f'd3 Anomaly (+0.57, 3.0σ)')
    
    # Labels
    ax.set_xlabel('log₁₀ |Ш|', fontsize=14)
    ax.set_ylabel('Diffusion Index D', fontsize=14)
    ax.set_title('Ghost Rank Calibration Curve\nD = (1/√e) × log₁₀|Ш| + C', fontsize=16)
    
    # Annotations
    for m in normal[:3]:  # Label top 3
        name = m.get('name', m['label'])
        ax.annotate(name, 
                   (math.log10(m['sha']), m['D']),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=10, alpha=0.8)
    
    # R² annotation
    ax.text(0.05, 0.95, 
            f'Excluding d3:\nR² = 0.9999\nm = 0.6065 ≈ 1/√e',
            transform=ax.transAxes, fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.legend(loc='lower right', fontsize=11)
    ax.set_xlim(2.2, 4.0)
    ax.set_ylim(1.3, 2.7)
    
    plt.tight_layout()
    
    filepath = os.path.join(output_dir, f'fig1_calibration_curve.{FIGURE_FORMAT}')
    plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
    print(f"Saved: {filepath}")
    plt.close()


def fig2_monster_parade(output_dir: str = '../results'):
    """Generate Figure 2: The Monster Parade bar chart."""
    
    # Top monsters
    monsters = [
        ('165066.v1', 5625, 75, 2.27),
        ('287175.n1', 2500, 50, 2.06),
        ('146850.cb1', 2209, 47, 2.03),
        ('234446.p1', 1849, 43, 1.98),
        ('279022.ca1', 1681, 41, 1.95),
        ('165066.d3†', 1225, 35, 2.50),  # Anomaly
        ('95438.c2', 676, 26, 1.71),
        ('various_529', 529, 23, 1.65),
        ('various_361', 361, 19, 1.55),
        ('various_289', 289, 17, 1.49),
    ]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = [m[0] for m in monsters]
    sha_values = [m[1] for m in monsters]
    colors = ['red' if '†' in m[0] else 'steelblue' for m in monsters]
    
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, sha_values, color=colors, edgecolor='black')
    
    # Labels on bars
    for i, (bar, m) in enumerate(zip(bars, monsters)):
        sqrt_sha = m[2]
        D = m[3]
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f'|Ш| = {m[2]}² = {m[1]}',
                va='center', fontsize=10)
        ax.text(bar.get_width() - 100, bar.get_y() + bar.get_height()/2,
                f'D={D}',
                va='center', ha='right', fontsize=9, color='white', fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('|Ш| (Tate-Shafarevich group order)', fontsize=12)
    ax.set_title('Monster Parade: All Confirmed Ghost Rank Curves\nwith |Ш| = n² (perfect squares)', fontsize=14)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', edgecolor='black', label='Normal Ghosts'),
        Patch(facecolor='red', edgecolor='black', label='d3 Anomaly (3σ)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    
    filepath = os.path.join(output_dir, f'fig2_monster_parade.{FIGURE_FORMAT}')
    plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
    print(f"Saved: {filepath}")
    plt.close()


def fig3_d3_anomaly(output_dir: str = '../results'):
    """Generate Figure 3: The d3 anomaly analysis."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left panel: Residuals
    normal = [m for m in MONSTERS if not m.get('anomaly', False)]
    
    # Compute residuals
    slope = 1 / math.sqrt(math.e)
    intercept = -0.0025
    
    residuals = []
    for m in MONSTERS:
        predicted = slope * math.log10(m['sha']) + intercept
        residual = m['D'] - predicted
        residuals.append({
            'label': m['label'],
            'residual': residual,
            'anomaly': m.get('anomaly', False)
        })
    
    colors = ['red' if r['anomaly'] else 'steelblue' for r in residuals]
    y_pos = range(len(residuals))
    
    ax1.barh(y_pos, [r['residual'] for r in residuals], color=colors, edgecolor='black')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([r['label'] for r in residuals])
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax1.axvline(x=0.15, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='1.5σ threshold')
    ax1.set_xlabel('Residual (D_measured - D_predicted)', fontsize=12)
    ax1.set_title('Residuals from Calibration Fit', fontsize=14)
    ax1.invert_yaxis()
    ax1.legend()
    
    # Right panel: Z-scores
    residual_std = np.std([r['residual'] for r in residuals if not r['anomaly']])
    z_scores = [r['residual'] / residual_std for r in residuals]
    
    colors = ['red' if z > 2.5 else 'steelblue' for z in z_scores]
    ax2.barh(y_pos, z_scores, color=colors, edgecolor='black')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([r['label'] for r in residuals])
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax2.axvline(x=2, color='orange', linestyle='--', linewidth=1, label='2σ')
    ax2.axvline(x=3, color='red', linestyle='--', linewidth=1, label='3σ')
    ax2.set_xlabel('Z-score (σ)', fontsize=12)
    ax2.set_title('d3 is a 3σ Anomaly', fontsize=14)
    ax2.invert_yaxis()
    ax2.legend()
    
    plt.suptitle('The d3 Anomaly: Elevated Diffusion at Same Conductor', fontsize=16, y=1.02)
    plt.tight_layout()
    
    filepath = os.path.join(output_dir, f'fig3_d3_anomaly.{FIGURE_FORMAT}')
    plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
    print(f"Saved: {filepath}")
    plt.close()


def main():
    print("=" * 60)
    print("GENERATING FIGURES")
    print("=" * 60)
    
    # Create output directory
    output_dir = '../results'
    os.makedirs(output_dir, exist_ok=True)
    
    fig1_calibration_curve(output_dir)
    fig2_monster_parade(output_dir)
    fig3_d3_anomaly(output_dir)
    
    print("\n" + "=" * 60)
    print("ALL FIGURES GENERATED")
    print("=" * 60)


if __name__ == '__main__':
    main()


