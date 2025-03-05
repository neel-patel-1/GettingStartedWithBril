import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# Read data from stdin
df = pd.read_csv(sys.stdin)

# Pivot the data for easier processing
df_pivot = df.pivot(index='benchmark', columns='run', values='result', )

#csv has format:
# Calculate percentage improvement
df_pivot['baseline'] = pd.to_numeric(df_pivot['baseline'], errors='coerce')
df_pivot['roundtrip'] = pd.to_numeric(df_pivot['roundtrip'], errors='coerce')
df_pivot['roundtrip_lvn_dce'] = pd.to_numeric(df_pivot['roundtrip_lvn_dce'], errors='coerce')
df_pivot['roundtrip'] = ((df_pivot['roundtrip']) / df_pivot['baseline'])
df_pivot['roundtrip_opt'] = (((df_pivot['roundtrip_lvn_dce']) / df_pivot['baseline']))

# Plotting
benchmarks = df_pivot.index
x = np.arange(len(benchmarks))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots(figsize=(15, 8))

# Create bars for DCE and LVN improvements
bars_dce = ax.bar(x - 0.5 * width, df_pivot['roundtrip'], width, label='Roundtrip')
bars_lvn = ax.bar(x + 0.5 * width, df_pivot['roundtrip_opt'], width, label='RountripOpt')

# Add labels, title, and legend
ax.set_xlabel('Benchmark', fontsize=12)
ax.set_ylabel('Dynamic Instruction Count (Normalized to Baseline)', fontsize=12)
#ax.set_title('Performance Improvements of DCE and LVN Over Baseline', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(benchmarks, rotation=90, fontsize=10)
ax.legend()
# ax.set_yscale('log')

# Add percentage values above bars
labeled_heights = set()
for bar in bars_dce + bars_lvn:
    height = bar.get_height()
    if height != 0 and height not in labeled_heights:  # Avoid zero bars and duplicate labels
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset text by 3 points
                    textcoords="offset points",
                    ha='center', va='bottom')
        labeled_heights.add(height)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.savefig('performance_loss.png')