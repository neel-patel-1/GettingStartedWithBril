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
      bb = [instr]
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
    print(f'bb: {bb[1]}', file=sys.stderr)
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
    else: # empty bb
      if index < len(bbs) - 1:
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
    else: # empty bb
      if index < len(bbs) - 1:
        if index in succ_map:
          succ_map[index].append(bbs[index + 1][1])
        else:
          succ_map[index] = [bbs[index + 1][1]]


prog = json.load(sys.stdin)
for function in prog['functions']:
  bbs = form_bbs(function)
  print(f'bbs: {bbs}', file=sys.stderr)
  form_predecessor_map(bbs)
  form_successor_map(bbs)
  print(f'bbs: {bbs}', file=sys.stderr)
  print(f'pred_map: {pred_map}', file=sys.stderr)
  print(f'succ_map: {succ_map}', file=sys.stderr)

