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

def create_outset(bb, bb_list):
  global succ_map
  outset = set()
  if bb[1] in succ_map:
    for succ in succ_map[bb[1]]:
      if bb_list[succ][1] in insets:
        for var in insets[bb_list[succ][1]]:
          outset.add(var)
  return outset



prog = json.load(sys.stdin)
for function in prog['functions']:
  outsets.clear()
  use_defs.clear()
  pred_map.clear()
  succ_map.clear()
  bbs = form_bbs(function)
  form_predecessor_map(bbs)
  form_successor_map(bbs)

  bbq = queue.Queue()
  for bb in bbs:
    bbq.put(bb)

  while not bbq.empty():
    bb = bbq.get()
    outset = create_outset(bb,bbs)
    # print(f'bb: {bb[1]} outset: {outset}')
    # print(f'bb: {bb[0]}')
    if bb[1] in insets:
      inset = insets[bb[1]]
    else:
      inset = set()
    new_inset = transfer(bb, outset)
    # print(f'bb: {bb[1]} new_inset: {new_inset}')
    if new_inset != inset or bb[1] not in insets:
      insets[bb[1]] = new_inset
      if bb[1] in pred_map:
        for pred in pred_map[bb[1]]:
          bbq.put(bbs[pred])

for bb in bbs:
  print(f'bb: {bb[1]} inset: {insets[bb[1]]}')