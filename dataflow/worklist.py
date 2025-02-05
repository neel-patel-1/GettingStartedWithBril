import json
import sys
import queue
from bb import form_bbs, form_predecessor_map, form_successor_map, pred_map, succ_map

insets = {}
outsets = {}
name2id = {}

def worklist(create_outset, transfer, function):
    outsets.clear()
    insets.clear()
    pred_map.clear()
    succ_map.clear()
    bbs = form_bbs(function)
    print(f'Predecessor map: {pred_map}', file=sys.stderr)
    form_successor_map(bbs)
    print(f'Successor map: {succ_map}', file=sys.stderr)

    bbq = queue.Queue()
    in_queue = set()  # Set to keep track of entries in the queue
    for index, bb in enumerate(bbs):
      bbq.put(index)
      in_queue.add(index)
      name2id[bb[1]] = index

    while not bbq.empty():
      bbid = bbq.get()
      in_queue.remove(bbid)  # Remove from in_queue when dequeued
      bb = bbs[bbid]
      outset = create_outset(bbid)
      if bb[1] in insets:
        inset = insets[bb[1]]
      else:
        inset = set()
      print(f'Running transfer on {bb[1]} with outset {outset}', file=sys.stderr)
      new_inset = transfer(bb, outset)
      if new_inset != inset or bb[1] not in insets:
        print(f'Updating inset for {bb[1]} from {inset} to {new_inset}', file=sys.stderr)
        insets[bb[1]] = new_inset
        if bb[1] in pred_map:
          for pred in pred_map[bb[1]]:
            if pred not in in_queue:  # Add to queue only if not already in there
              print(f'Readding {bbs[pred][1]} due to {bb[1]} who\'s inset is now {new_inset}', file=sys.stderr)
              bbq.put(pred)
              in_queue.add(pred)
    return bbs