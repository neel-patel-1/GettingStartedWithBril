#!/usr/bin/env python3
import re
import sys
import matplotlib.pyplot as plt
import numpy as np

def parse_file(filename):
    """
    Parses the input file and returns a list of tuples:
    (benchmark_label, mem2reg_time, licm_time)
    """
    benchmarks = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for the start of a benchmark block.
        m = re.match(r"^Running benchmark for (.+)\.\.\.$", line)
        if m:
            bench_path = m.group(1).strip()
            # Extract the benchmark name from the path (last component)
            bench_label = bench_path.split('/')[-1]
            mem2reg_time = None
            licm_time = None
            # Search subsequent lines for the two "[INFO] Normalized time:" entries.
            j = i + 1
            while j < len(lines) and (mem2reg_time is None or licm_time is None):
                norm_match = re.search(r"\[INFO\] Normalized time:\s*([\d\.]+)", lines[j])
                if norm_match:
                    time_val = float(norm_match.group(1))
                    if mem2reg_time is None:
                        mem2reg_time = time_val
                    else:
                        licm_time = time_val
                j += 1
            if mem2reg_time is not None and licm_time is not None:
                benchmarks.append((bench_label, mem2reg_time, licm_time))
            i = j
        else:
            i += 1
    return benchmarks

def plot_benchmarks(benchmarks):
    """
    Plots a grouped bar chart.
    - X-axis: benchmark names
    - Series 1 (mem2reg): normalized to 1.0
    - Series 2 (licm): ratio = licm_time / mem2reg_time
    """
    labels = [b[0] for b in benchmarks]
    mem2reg = [b[1] for b in benchmarks]
    licm = [b[2] for b in benchmarks]
    # Compute ratio: licm normalized to mem2reg.
    ratio = [l / m for l, m in zip(licm, mem2reg)]
    # mem2reg baseline is 1.0 for each benchmark.
    mem2reg_norm = [1.0] * len(mem2reg)

    x = np.arange(len(labels))
    width = 0.35  # Width of each bar

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, mem2reg_norm, width, label='mem2reg (baseline)')
    rects2 = ax.bar(x + width/2, ratio, width, label='licm (normalized)')

    ax.set_ylabel('Normalized Time (relative to mem2reg)')
    ax.set_title('Benchmark Performance Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()

    # Annotate the licm bars with their ratio value.
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    fig.tight_layout()
    plt.savefig('benchmark_comparison.png')

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    benchmarks = parse_file(results_file)

    if not benchmarks:
        print("No benchmarks found in the file.")
        sys.exit(1)

    print("Parsed benchmarks:")
    for bench in benchmarks:
        print(f"Benchmark: {bench[0]}, mem2reg time: {bench[1]}, licm time: {bench[2]}, ratio: {bench[2]/bench[1]:.2f}")

    plot_benchmarks(benchmarks)

if __name__ == "__main__":
    main()