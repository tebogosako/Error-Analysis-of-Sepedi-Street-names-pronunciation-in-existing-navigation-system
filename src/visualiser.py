
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.patches import Patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import *

print("=" * 70)
print("CREATING NEW VISUALIZATIONS")
print("=" * 70)

# Find the latest results file
output_dir = OUTPUT_DIR
run_dirs = sorted([d for d in output_dir.glob('run_*') if d.is_dir()], reverse=True)

if not run_dirs:
    print("No run directories found.")
    print("Please run run_analysis_fixed.py first")
    sys.exit(1)

latest_run = run_dirs[0]
print(f"Using data from: {latest_run}")

# Load the data
df = pd.read_csv(latest_run / 'full_results.csv')
print(f"Loaded {len(df)} rows of data")
print(f"Columns: {list(df.columns)}")

# Create visualizations directory
viz_dir = latest_run / 'visualizations'
viz_dir.mkdir(parents=True, exist_ok=True)
print(f"Saving visualizations to: {viz_dir}")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# 1. WER by Participant (with individual points)
print("\nCreating WER by Participant...")
fig, ax = plt.subplots(figsize=(12, 6))

# Box plot showing distribution
participants = df['participant'].unique()
data = [df[df['participant'] == p]['wer'].values for p in participants]
bp = ax.boxplot(data, labels=participants, patch_artist=True)

# Color the boxes
colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
for patch, color in zip(bp['boxes'], colors[:len(participants)]):
    patch.set_facecolor(color)

# Add individual points
for i, p in enumerate(participants):
    y = df[df['participant'] == p]['wer'].values
    x = np.random.normal(i+1, 0.04, size=len(y))
    ax.scatter(x, y, alpha=0.6, s=50, color='black')

ax.set_title('Word Error Rate by Participant\n(Higher = More Errors)', fontsize=14, fontweight='bold')
ax.set_xlabel('Participant', fontsize=12)
ax.set_ylabel('WER (0 = Perfect, 1 = Completely Wrong)', fontsize=12)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)

# Add mean values on top
for i, p in enumerate(participants):
    mean_val = df[df['participant'] == p]['wer'].mean()
    ax.text(i+1, mean_val + 0.02, f'mu={mean_val:.3f}', 
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(viz_dir / 'wer_by_participant_box.png', dpi=300)
plt.close()
print(f"Saved: wer_by_participant_box.png")

# 2. Pronunciation Score by Participant
print("\nCreating Pronunciation Score chart...")
fig, ax = plt.subplots(figsize=(12, 6))

# Bar chart with error bars
participant_scores = df.groupby('participant')['pronunciation_score'].agg(['mean', 'std']).reset_index()
participant_scores = participant_scores.sort_values('mean', ascending=False)

bars = ax.bar(participant_scores['participant'], participant_scores['mean'], 
              yerr=participant_scores['std'], capsize=5, 
              color=['#2ecc71' if i == 0 else '#3498db' for i in range(len(participant_scores))])

# Add value labels
for bar, score in zip(bars, participant_scores['mean']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{score:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_title('Pronunciation Score by Participant\n(Higher = Better Pronunciation)', fontsize=14, fontweight='bold')
ax.set_xlabel('Participant', fontsize=12)
ax.set_ylabel('Pronunciation Score (0-1)', fontsize=12)
ax.set_ylim(0, 1.1)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(viz_dir / 'pronunciation_scores.png', dpi=300)
plt.close()
print(f"Saved: pronunciation_scores.png")

# 3. Street Difficulty Ranking
print("\nCreating Street Difficulty chart...")
fig, ax = plt.subplots(figsize=(14, 6))

street_wer = df.groupby('street')['wer'].mean().sort_values(ascending=False)
colors = ['#e74c3c' if i < 3 else '#f39c12' if i < 6 else '#2ecc71' 
          for i in range(len(street_wer))]

bars = ax.bar(range(len(street_wer)), street_wer.values, color=colors)
ax.set_xticks(range(len(street_wer)))
ax.set_xticklabels(street_wer.index, rotation=45, ha='right')

# Add value labels
for bar, value in zip(bars, street_wer.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{value:.3f}', ha='center', va='bottom', fontsize=9)

ax.set_title('Street Difficulty Ranking\n(Higher WER = More Difficult to Pronounce)', fontsize=14, fontweight='bold')
ax.set_xlabel('Street Name', fontsize=12)
ax.set_ylabel('Average WER', fontsize=12)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3, axis='y')

# Add color legend
legend_elements = [
    Patch(facecolor="#c8ff00", label='Most Difficult'),
    Patch(facecolor="#05c6f6", label='Moderately Difficult'),
    Patch(facecolor="#f71ce5", label='Easiest')
]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig(viz_dir / 'street_difficulty.png', dpi=300)
plt.close()
print(f"Saved: street_difficulty.png")

# 4. Heatmap: Participant vs Street
print("\nCreating Heatmap...")
fig, ax = plt.subplots(figsize=(14, 8))

# Pivot table
pivot = df.pivot_table(index='participant', columns='street', values='wer', aggfunc='mean')

# Create heatmap
sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdYlGn_r', 
            cbar_kws={'label': 'WER (Lower = Better)'},
            linewidths=0.5, linecolor='white', ax=ax)

ax.set_title('WER Heatmap: Participant vs Street\n(Red = High Error, Green = Low Error)', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Street', fontsize=12)
ax.set_ylabel('Participant', fontsize=12)

plt.tight_layout()
plt.savefig(viz_dir / 'wer_heatmap.png', dpi=300)
plt.close()
print(f"Saved: wer_heatmap.png")

# 5. Error Type Distribution (Pie Chart)
print("\nCreating Error Distribution...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Overall error distribution
error_counts = df['error_type'].value_counts()
colors_pie = ['#2ecc71', '#f1c40f', '#e74c3c']
explode = (0.05, 0.05, 0.05)

ax1.pie(error_counts.values, labels=error_counts.index, autopct='%1.1f%%',
        colors=colors_pie[:len(error_counts)], explode=explode[:len(error_counts)],
        startangle=90, textprops={'fontsize': 12})
ax1.set_title('Overall Error Distribution', fontsize=14, fontweight='bold')

# Error distribution by participant
error_by_participant = pd.crosstab(df['participant'], df['error_type'], normalize='index') * 100
error_by_participant.plot(kind='bar', stacked=True, ax=ax2, color=colors_pie[:len(error_by_participant.columns)])

ax2.set_title('Error Distribution by Participant', fontsize=14, fontweight='bold')
ax2.set_xlabel('Participant', fontsize=12)
ax2.set_ylabel('Percentage (%)', fontsize=12)
ax2.legend(title='Error Type', bbox_to_anchor=(1.05, 1), loc='upper left')
ax2.set_ylim(0, 100)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(viz_dir / 'error_distribution.png', dpi=300)
plt.close()
print(f"Saved: error_distribution.png")

# 6. Radar Chart: Participant Comparison
print("\nCreating Radar Chart...")

# Calculate metrics for radar
metrics = ['wer', 'cer', 'pronunciation_score']
# Reverse WER and CER for radar (higher is better)
df_radar = df.copy()
df_radar['wer_reversed'] = 1 - df_radar['wer']
df_radar['cer_reversed'] = 1 - df_radar['cer']

# Aggregate by participant
radar_data = df_radar.groupby('participant')[['wer_reversed', 'cer_reversed', 'pronunciation_score']].mean()

# Create radar chart
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# Number of variables
N = len(radar_data.columns)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # Close the loop

# Plot each participant
colors_radar = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
for idx, (participant, row) in enumerate(radar_data.iterrows()):
    values = row.values.tolist()
    values += values[:1]  # Close the loop
    ax.plot(angles, values, 'o-', linewidth=2, label=participant, color=colors_radar[idx % len(colors_radar)])
    ax.fill(angles, values, alpha=0.1, color=colors_radar[idx % len(colors_radar)])

# Set the labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(['Low WER', 'Low CER', 'High Pronunciation Score'], fontsize=12)
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
ax.grid(True)

ax.set_title('Participant Performance Radar Chart\n(Higher Values = Better Performance)', 
            fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

plt.tight_layout()
plt.savefig(viz_dir / 'radar_chart.png', dpi=300)
plt.close()
print(f"Saved: radar_chart.png")

# 7. Scatter Plot: Duration vs Score
print("\nCreating Duration vs Score scatter plot...")
fig, ax = plt.subplots(figsize=(12, 6))

# Calculate duration difference
df['duration_diff'] = df['participant_duration'] - df['apple_duration']

# Color by participant
colors_scatter = {'participant_1': '#2ecc71', 'participant_2': '#3498db', 
                  'participant_3': '#e74c3c', 'participant_4': '#f39c12'}

for participant in df['participant'].unique():
    mask = df['participant'] == participant
    ax.scatter(df[mask]['duration_diff'], df[mask]['pronunciation_score'], 
               label=participant, alpha=0.7, s=100, 
               color=colors_scatter.get(participant, 'gray'))

ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Score Threshold')
ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)

ax.set_title('Duration Difference vs Pronunciation Score\n(Negative = Participant Shorter, Positive = Participant Longer)', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Duration Difference (seconds)', fontsize=12)
ax.set_ylabel('Pronunciation Score (0-1)', fontsize=12)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)
ax.legend(loc='best')

plt.tight_layout()
plt.savefig(viz_dir / 'duration_vs_score.png', dpi=300)
plt.close()
print(f"Saved: duration_vs_score.png")

# 8. Pitch Analysis
print("\nCreating Pitch Analysis...")
fig, ax = plt.subplots(figsize=(12, 6))

# Calculate pitch difference
df['pitch_diff'] = df['participant_pitch'] - df['apple_pitch']

# Color by participant
for participant in df['participant'].unique():
    mask = df['participant'] == participant
    ax.scatter(df[mask]['pitch_diff'], df[mask]['pronunciation_score'], 
               label=participant, alpha=0.7, s=100,
               color=colors_scatter.get(participant, 'gray'))

ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Score Threshold')
ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)

ax.set_title('Pitch Difference vs Pronunciation Score\n(Positive = Participant Higher Pitch)', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Pitch Difference (Hz)', fontsize=12)
ax.set_ylabel('Pronunciation Score (0-1)', fontsize=12)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)
ax.legend(loc='best')

plt.tight_layout()
plt.savefig(viz_dir / 'pitch_analysis.png', dpi=300)
plt.close()
print(f"Saved: pitch_analysis.png")

# Summary
print("\n" + "=" * 70)
print("ALL VISUALIZATIONS CREATED")
print("=" * 70)

print(f"\nVisualizations saved to: {viz_dir}")
print("\nCreated visualizations:")
