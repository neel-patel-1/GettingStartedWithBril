import json
import sys
import queue
from bb import form_bbs, form_predecessor_map, form_successor_map, pred_map, succ_map

insets = {}
outsets = {}
name2id = {}

def worklist():
  prog = json.load(sys.stdin)
  for function in prog['functions']:
    outsets.clear()
    insets.clear()
    pred_map.clear()
    succ_map.clear()
    bbs = form_bbs(function)
    print(f'Predecessor map: {pred_map}', file=sys.stderr)
    form_successor_map(bbs)
    print(f'Successor map: {succ_map}', file=sys.stderr)