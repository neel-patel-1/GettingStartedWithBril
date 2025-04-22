#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

LABEL_RE = re.compile(r'^(\.[A-Za-z0-9_\.]+):\s*$')

def find_labels(lines):
    """Return list of (idx, label_name) for every label decl."""
    labels = []
    for idx, line in enumerate(lines):
        m = LABEL_RE.match(line)
        if m:
            labels.append((idx, m.group(1)))
    return labels

def extract_segments(lines, labels):
    """
    For each adjacent pair of label decls (L1 at i, L2 at j),
    record the raw lines between them (i+1 .. j-1).
    """
    occs = defaultdict(list)
    for (i, lab1), (j, lab2) in zip(labels, labels[1:]):
        block = lines[i+1:j]
        occs[(lab1, lab2)].append((i, j, block))
    return occs

def compute_canonical(occs):
    """
    For each (lab1,lab2), if there's at least one non-empty block
    and all non-empty blocks are identical, record that as canonical.
    """
    canon = {}
    for key, chunks in occs.items():
        # strip out blank-only chunks
        non_empty = [c for (_,_,c) in chunks if any(l.strip() for l in c)]
        if non_empty and all(non_empty[0] == c for c in non_empty[1:]):
            canon[key] = non_empty[0]
    return canon

def fill_and_emit(lines, labels, occs, canon):
    """
    Walk through the file.  Whenever you hit a label at idx i
    that’s followed by another label in labels, and (lab1,lab2) in canon,
    emit:
      - the label line
      - either the original non-empty block (if present) or the canon block
    then skip ahead to that next label.
    Otherwise just emit the current line.
    """
    # build quick lookups
    label_at = {i: lab for i, lab in labels}
    next_label = {i: j for (i,_), (j,_) in zip(labels, labels[1:])}

    out = []
    i = 0
    while i < len(lines):
        if i in label_at and i in next_label:
            lab1 = label_at[i]
            j = next_label[i]
            lab2 = label_at[j]
            key = (lab1, lab2)
            if key in canon:
                # emit the label itself
                out.append(lines[i])
                # check original between i+1 and j
                orig = lines[i+1:j]
                if any(l.strip() for l in orig):
                    # has its own code → keep it
                    out.extend(orig)
                else:
                    # empty → fill with canonical
                    out.extend(canon[key])
                # skip ahead to j
                i = j
                continue

        # default: just emit this line
        out.append(lines[i])
        i += 1

    return out

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        lines = f.readlines()

    labels = find_labels(lines)
    occs   = extract_segments(lines, labels)
    canon  = compute_canonical(occs)
    out    = fill_and_emit(lines, labels, occs, canon)

    sys.stdout.write(''.join(out))

if __name__ == "__main__":
    main()
