#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def load_ir(path):
    with open(path, 'r') as f:
        return json.load(f)

def is_label_stmt(stmt):
    # A pure label declaration has exactly one key "label"
    return isinstance(stmt, dict) and stmt.keys() == {"label"}

def find_label_positions(ir):
    # Return list of (index, label_name) for each label stmt
    return [(i, stmt["label"]) for i, stmt in enumerate(ir) if is_label_stmt(stmt)]

def extract_segments(ir, labels):
    """
    For each adjacent pair of labels (L1 at i, L2 at j), record:
      segments[(L1,L2)] → list of instruction‐lists between them
      occs    [(L1,L2)] → list of (i, j) positions
    """
    segments = defaultdict(list)
    occs     = defaultdict(list)

    for (i, lab1), (j, lab2) in zip(labels, labels[1:]):
        block = ir[i+1:j]
        # keep only non‐label statements
        instrs = [stmt for stmt in block if not is_label_stmt(stmt)]
        segments[(lab1, lab2)].append(instrs)
        occs[(lab1, lab2)].append((i, j))

    return segments, occs

def compute_canonical(segments):
    """
    For each pair (L1,L2), if there's ≥1 non‐empty block and
    all non‐empty blocks are identical, record that as canonical.
    """
    canon = {}
    for key, lists in segments.items():
        non_empty = [lst for lst in lists if lst]
        if non_empty and all(lst == non_empty[0] for lst in non_empty[1:]):
            canon[key] = non_empty[0]
    return canon

def fill_ir(ir, labels, occs, canon):
    """
    Walk through IR. Whenever you hit label@i with next label@j where
    (lab1,lab2) in canon,
      • emit the label stmt
      • if original block non‐empty, emit it; else emit canon[(lab1,lab2)]
      • skip ahead to j
    Otherwise just copy stmt[i].
    """
    label_at = {i: lab for i, lab in labels}
    next_idx = {i: j for (i,_), (j,_) in zip(labels, labels[1:])}

    out = []
    i = 0
    n = len(ir)
    while i < n:
        if i in label_at and i in next_idx:
            lab1 = label_at[i]
            j    = next_idx[i]
            lab2 = label_at[j]
            key  = (lab1, lab2)
            if key in canon:
                # emit the label itself
                out.append(ir[i])
                # original between i+1 and j
                orig = [stmt for stmt in ir[i+1:j] if not is_label_stmt(stmt)]
                if orig:
                    out.extend(orig)
                else:
                    out.extend(canon[key])
                # jump to the next label
                i = j
                continue

        # default: copy current stmt
        out.append(ir[i])
        i += 1

    return out

def main():
    if len(sys.argv) not in (2,3):
        print(f"Usage: {sys.argv[0]} <in.json> [<out.json>]", file=sys.stderr)
        sys.exit(1)

    in_path  = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) == 3 else None

    ir       = load_ir(in_path)
    labels   = find_label_positions(ir)
    segments, occs = extract_segments(ir, labels)
    canon    = compute_canonical(segments)
    new_ir   = fill_ir(ir, labels, occs, canon)

    out_data = json.dumps(new_ir, indent=2)
    if out_path:
        with open(out_path, 'w') as f:
            f.write(out_data)
    else:
        print(out_data)

if __name__ == "__main__":
    main()
