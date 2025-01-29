import json
from collections import OrderedDict
import sys

TERMINATORS = 'br', 'jmp', 'ret'
num_bbs = 0
num_edges = 0
num_functions = 0

def form_bbs(data):
  global num_bbs, num_functions
  functions = data['functions']
  bbs = []
  for function in functions:
    instrs = function['instrs']
    bb = []
    for instr in instrs:
      bb.append(instr)
      if 'op' in instr:
        if instr['op'] in TERMINATORS:
          bbs.append(bb)
          bb = []
          num_bbs += 1
    if bb:
      bbs.append(bb)
      num_bbs += 1
    num_functions += 1
  return bbs

# to form edges, it may be useful to have a mapping from labels to blocks
block_map = OrderedDict()
def form_bb_map(bbs):
  for bb in bbs:
    if 'label' in bb[0]:
      name = bb[0]['label']
      block = bb[1:]
    else:
      name = 'b' + str(len(block_map))
      block = bb
    if(len(block) > 0):
      block_map[name] = block
    # print(f"Name: {name}, Block: {block}")

cfg = OrderedDict()
def form_cfg():
  global num_edges, cfg
  for label, block in block_map.items():
    # print(f"Label: {label}, Block: {block}")
    try:
      if block[-1]['op'] in ('jmp', 'br'):
        succ = block[-1]['labels']
        successors = []
        for slbl in succ:
          num_edges += 1
          successors.append(slbl)
        cfg[label] = successors
      elif (label, block) == list(block_map.items())[-1]:
        cfg[label] = []
      else:
        num_edges += 1
        # print(f"Block map: {block_map}")
        next_block = list(block_map.values())[list(block_map.keys()).index(label) + 1]
        cfg[label] = [next_block]
    except:
      print(f"Error: {label}, {block}")
  print(cfg)

def count_add_instructions(data):
  count = 0
  for function in data['functions']:
    for instr in function['instrs']:
      if 'op' in instr:
        if instr['op'] == 'add':
          count += 1
  return count

data = json.load(sys.stdin)
bbs = form_bbs(data)
form_bb_map(bbs)
form_cfg()
add_instrs = count_add_instructions(data)

print(f"Number of functions: {num_functions}")
print(f"Number of basic blocks: {num_bbs}")
print(f"Number of edges: {num_edges}")
print(f"Number of add instructions: {add_instrs}")
