import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}
insets = {}
outsets = {}
pred_map = {}
succ_map = {}

counter = 0
def get_fresh_bb_name():
  global counter
  counter += 1
  new_name = f'b{counter}'
  return new_name

def transfer(bb, outset):
  inset = set(outset)
  for instr in reversed(bb[0]):
    if 'op' in instr:
      if 'dest' in instr:
        inset.discard(instr['dest'])
      if 'args' in instr:
        for arg in instr['args']:
          inset.add(arg)
  return inset

def remove_dead(bb, outset):
  p_a = outset
  new_bb_r = []
  for i in reversed(bb[0]):
    if 'dest' in i and 'op' != 'call' and i['dest'] not in p_a:
      continue
    else:
      new_bb_r.append(i)
      if 'args' in i:
        for arg in i['args']:
          p_a.add(arg)
  new_bb = (list(reversed(new_bb_r)), bb[1], bb[2], bb[3])
  return new_bb


def form_bbs(function):
  num_bbs = 0
  bbs = []
  instrs = function['instrs']
  bb = []
  bb_label = 'Entry'
  for instr in instrs:
    bb.append(instr)
    if 'label' in instr and len(bb) == 1:
      bb_label = instr['label']
    if 'op' in instr:
      if instr['op'] in TERMINATORS:
        if bb_label == None:
          bb_label = get_fresh_bb_name()
        bbs.append((bb, bb_label,None,None))
        bb = []
        num_bbs += 1
        bb_label = None
    if 'label' in instr and len(bb) > 1:
      if bb_label == None:
        bb_label = get_fresh_bb_name()
      bb = bb[:-1]
      bbs.append((bb, bb_label,None,None))
      bb = []
      bb_label = instr['label']
      num_bbs += 1
  if bb:
    if bb_label == None:
      bb_label = get_fresh_bb_name()
    bbs.append((bb, bb_label,None,None))
    num_bbs += 1
  return (bbs)

def form_predecessor_map(bbs):
  global pred_map
  for index, bb in enumerate(bbs):
    if 'op' in bb[0][-1]:
      if bb[0][-1]['op'] in TERMINATORS:
        if 'labels' in bb[0][-1]:
          for label in bb[0][-1]['labels']:
            if label in pred_map:
              pred_map[label].append(index)
            else:
              pred_map[label] = [index]
      elif index < len(bbs) - 1:
        if bbs[index + 1][1] in pred_map:
          pred_map[bbs[index + 1][1]].append(index)
        else:
          pred_map[bbs[index + 1][1]] = [index]

def form_successor_map(bbs):
  global succ_map
  for index, bb in enumerate(bbs):
    if 'op' in bb[0][-1]:
      if bb[0][-1]['op'] in TERMINATORS:
        if 'labels' in bb[0][-1]:
          for label in bb[0][-1]['labels']:
            if index in succ_map:
              succ_map[index].append(label)
            else:
              succ_map[index] = [label]
      elif index < len(bbs) - 1:
        if index in succ_map:
          succ_map[index].append(bbs[index + 1][1])
        else:
          succ_map[index] = [bbs[index + 1][1]]

def create_outset(index):
  global succ_map
  outset = set()
  if index in succ_map:
    for succ in succ_map[index]:
      if succ in insets:
        for var in insets[succ]:
          outset.add(var)
  return outset

name2id = {}

prog = json.load(sys.stdin)
for function in prog['functions']:
  outsets.clear()
  use_defs.clear()
  pred_map.clear()
  succ_map.clear()
  bbs = form_bbs(function)
  form_predecessor_map(bbs)
  print(f'Predecessor map: {pred_map}', file=sys.stderr)
  form_successor_map(bbs)

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

  new_bbs = []
  for index, bb in enumerate(bbs):
    outset = create_outset(index)
    print(f'bb: {bb[1]} outset: {outset} inset: {insets[bb[1]]}', file=sys.stderr)
    new_bb = remove_dead(bb, outset)
    new_bbs.append(new_bb)

  function['instrs'] = []
  for bb in new_bbs:
    function['instrs'] += bb[0]

print(json.dumps(prog))

