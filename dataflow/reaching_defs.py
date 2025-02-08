import json
import sys
from collections import OrderedDict

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}

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
      bb_label = instr['label']
      num_bbs += 1
  if bb:
    if bb_label == None:
      bb_label = get_fresh_bb_name()
    bbs.append((bb, bb_label,None,None))
    num_bbs += 1
  return (bbs)

def form_predecessor_map(bbs):
  pred_map = {}
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
  return pred_map

def get_repr(index,bb):
  bb_instnum = bb[1] + str(index)
  return bb_instnum

def transfer(bb, inset):
  insts = bb[0]
  outset = dict(inset)
  for index, inst in enumerate(insts):
    if 'args' in inst:
      use_defs[(get_repr(index,bb))] = outset
    if 'dest' in inst:
      outset[inst['dest']] = get_repr(index,bb)
  return outset

outsets = {}
prog = json.load(sys.stdin)
for function in prog['functions']:
  outsets.clear()
  use_defs.clear()
  bbs = form_bbs(function)
  pred_map = form_predecessor_map(bbs)

inset = transfer(bbs[0], dict())
print(inset)