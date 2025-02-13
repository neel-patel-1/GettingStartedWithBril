import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# Read data from stdin
df = pd.read_csv(sys.stdin)

# Pivot the data for easier processing
df_pivot = df.pivot(index='benchmark', columns='run', values='result')

# Calculate percentage improvement
df_pivot['dce_improvement'] = ((df_pivot['baseline'] - df_pivot['dce']) / df_pivot['baseline']) * 100
df_pivot['lvn_improvement'] = ((df_pivot['baseline'] - df_pivot['lvn_dce']) / df_pivot['baseline']) * 100
df_pivot['live_improvement'] = ((df_pivot['baseline'] - df_pivot['lvn_dce_live']) / df_pivot['baseline']) * 100
df_pivot['const_improvement'] = ((df_pivot['baseline'] - df_pivot['lvn_dce_live_const']) / df_pivot['baseline']) * 100

# Plotting
benchmarks = df_pivot.index
x = np.arange(len(benchmarks))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots(figsize=(15, 8))

# Create bars for DCE and LVN improvements
# bars_dce = ax.bar(x - width/2, df_pivot['dce_improvement'], width, label='DCE Improvement')
# bars_lvn = ax.bar(x + width/2, df_pivot['lvn_improvement'], width, label='LVN Improvement')
# bars_live = ax.bar(x + width, df_pivot['live_improvement'], width, label='Live Improvement')
bars_dce = ax.bar(x - 1.5 * width, df_pivot['dce_improvement'], width, label='DCE Improvement')
bars_lvn = ax.bar(x - 0.5 * width, df_pivot['lvn_improvement'], width, label='LVN Improvement')
bars_live = ax.bar(x + 0.5 * width, df_pivot['live_improvement'], width, label='Live Improvement')
bars_const = ax.bar(x + 1.5 * width, df_pivot['const_improvement'], width, label='Const Improvement')

# Add labels, title, and legend
ax.set_xlabel('Benchmark', fontsize=12)
ax.set_ylabel('Percent Dynamic Instruction Reduction (%)', fontsize=12)
#ax.set_title('Performance Improvements of DCE and LVN Over Baseline', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(benchmarks, rotation=90, fontsize=10)
ax.legend()

# Add percentage values above bars
labeled_heights = set()
for bar in bars_dce + bars_lvn + bars_live + bars_const:
    height = bar.get_height()
    if height != 0 and height not in labeled_heights:  # Avoid zero bars and duplicate labels
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset text by 3 points
                    textcoords="offset points",
                    ha='center', va='bottom')
        labeled_heights.add(height)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.savefig('performance_improvements.png')