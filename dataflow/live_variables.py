import json
import sys
import queue
from worklist import worklist


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

def create_outset(index):
  global succ_map
  outset = set()
  if index in succ_map:
    for succ in succ_map[index]:
      if succ in insets:
        for var in insets[succ]:
          outset.add(var)
  return outset

worklist()