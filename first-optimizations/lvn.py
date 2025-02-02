import json
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

expr_num_map = {}

def get_table_repr(expr):
  if 'op' in expr:
    print(f"op: {expr['op']}")
  elif 'label' in expr:
    print(f"label: {expr['label']}")
  else:
    print(f"{expr}")


prog = json.load(sys.stdin)
for function in prog['functions']:
  bbinfo = form_bbs(function) # get the bbs
  bbs = bbinfo[0]
  function['instrs'] = [] # clear the instrs
  for bb in bbs:
    for instr in bb:
      get_table_repr(instr)

# print(json.dumps(prog, indent=2))
