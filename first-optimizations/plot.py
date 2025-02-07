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
df_pivot['lvn_improvement'] = ((df_pivot['baseline'] - df_pivot['lvn']) / df_pivot['baseline']) * 100

# Plotting
benchmarks = df_pivot.index
x = np.arange(len(benchmarks))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots(figsize=(15, 8))

# Create bars for DCE and LVN improvements
bars_dce = ax.bar(x - width/2, df_pivot['dce_improvement'], width, label='DCE Improvement')
bars_lvn = ax.bar(x + width/2, df_pivot['lvn_improvement'], width, label='LVN Improvement')

# Add labels, title, and legend
ax.set_xlabel('Benchmark', fontsize=12)
ax.set_ylabel('Percent Dynamic Instruction Reduction (%)', fontsize=12)
#ax.set_title('Performance Improvements of DCE and LVN Over Baseline', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(benchmarks, rotation=90, fontsize=10)
ax.legend()

# Add percentage values above bars
for bar in bars_dce + bars_lvn:
    height = bar.get_height()
    if height != 0:  # Avoid zero bars
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset text by 3 points
                    textcoords="offset points",
                    ha='center', va='bottom')

# Adjust layout
plt.tight_layout()

# Show the plot
plt.savefig('performance_improvements.png')