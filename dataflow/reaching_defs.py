import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}
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
  # print(f'pred_map: {pred_map}')


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


def get_repr(index,bb):
  bb_instnum = bb[1] + "_" + str(index)
  return bb_instnum

def transfer(bb, inset):
  insts = bb[0]
  outset = dict(inset)
  for index, inst in enumerate(insts):
    if 'args' in inst:
      use_defs[(get_repr(index,bb))] = outset
    if 'dest' in inst:
      outset[inst['dest']] = [get_repr(index,bb)]
  return outset

def create_inset(bb,bb_list):
  global pred_map
  inset = dict()
  if bb[1] in pred_map:
    for pred in pred_map[bb[1]]:
      if bb_list[pred][1] in outsets:
        for key in outsets[bb_list[pred][1]]:
          if key in inset:
            inset[key] = inset[key] + outsets[bb_list[pred][1]][key]
          else:
            inset[key] = outsets[bb_list[pred][1]][key]
    # print(f'bb: {bb[1]} inset: {inset}')
  return inset


prog = json.load(sys.stdin)
for function in prog['functions']:
  outsets.clear()
  use_defs.clear()
  pred_map.clear()
  succ_map.clear()
  bbs = form_bbs(function)
  if 'args' in function:
    function_args = function['args']
  else:
    function_args = None
  form_predecessor_map(bbs)
  form_successor_map(bbs)

  bbq = queue.Queue()
  for bb in bbs:
    bbq.put(bb)

  while not bbq.empty():
    bb = bbq.get()
    inset = create_inset(bb,bbs)
    if bb[1] == 'Entry' and function_args:
      for arg in function_args:
        inset[arg['name']] = 'Entry_Args'
        # print(f'bb: {bb[1]} inset: {inset}')
    if bb[1] in outsets:
      outset = outsets[bb[1]]
    else:
      outset = dict()
    new_outset = transfer(bb, inset)
    if new_outset != outset:
      outsets[bb[1]] = new_outset
      if bb[1] in succ_map:
        for succ in succ_map[bb[1]]:
          bbq.put(bbs[succ])
      # print(f'bb: {bb[1]} outset: {new_outset}')

  print(f"Function: {function['name']}")
  print(f"Use: Defs")
  for use in use_defs:
    print(f"{use}: {use_defs[use]}")