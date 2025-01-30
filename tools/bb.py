import json
from collections import OrderedDict
import sys

TERMINATORS = 'br', 'jmp', 'ret'

def form_bbs(function):
  num_bbs = 0
  bbs = []
  instrs = function['instrs']
  bb = []
  for instr in instrs:
    bb.append(instr)
    if 'op' in instr:
      if instr['op'] in TERMINATORS:
        bbs.append(bb)
        bb = []
        num_bbs += 1
    if 'label' in instr and len(bb) > 1:
      bb = bb[:-1]
      bbs.append(bb)
      bb = [instr]
      num_bbs += 1
  if bb:
    bbs.append(bb)
    num_bbs += 1
  return (bbs, num_bbs)

# to form edges, it may be useful to have a mapping from labels to blocks
def form_bb_map(bbs):
  block_map = OrderedDict()
  for bb in bbs:
    if 'label' in bb[0]:
      name = bb[0]['label']
      block = bb[1:]
    else:
      name = 'b' + str(len(block_map))
      block = bb
    if(len(block) > 0):
      block_map[name] = block
  return block_map

def form_cfg(block_map):
  num_edges = 0
  cfg = OrderedDict()
  for label, block in block_map.items():
    try:
      if block[-1]['op'] in ('jmp', 'br'):
        succ = block[-1]['labels']
        successors = []
        for slbl in succ:
          num_edges += 1
          successors.append(slbl)
        cfg[label] = successors
      elif block[-1]['op'] == 'ret':
        cfg[label] = []
      elif (label, block) == list(block_map.items())[-1]:
        cfg[label] = []
      else:
        num_edges += 1
        next_block = list(block_map.keys())[list(block_map.keys()).index(label) + 1]
        cfg[label] = [next_block]
    except:
      print(f"Error: {label}, {block}")
  return (cfg, num_edges)

def count_add_instructions(function):
  count = 0
  for instr in function['instrs']:
    if 'op' in instr:
      if instr['op'] == 'add':
        count += 1
  return count

data = json.load(sys.stdin)
print(f"Number of functions: {len(data['functions'])}")
for function in data['functions']:
  bbinfo = form_bbs(function)
  block_map = form_bb_map(bbinfo[0])
  (cfg, num_edges) = form_cfg(block_map)
  print(f"Function: {function['name']}, Number of basic blocks: {bbinfo[1]}, Number of edges in CFG: {num_edges}")
  print(f"CFG: {cfg}")
  add_instrs = count_add_instructions(function)
  print(f"Number of add instructions: {add_instrs}")