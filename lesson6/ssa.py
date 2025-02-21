import json
import sys

TERMINATORS = 'br', 'jmp', 'ret'
defs = {}

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
  bb_label = instrs[0]['label'] if 'label' in instrs[0] else 'Entry'
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
        print(f'bb: {bb}', file=sys.stderr)
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

prog = json.load(sys.stdin)
for function in prog['functions']:
  vars = set()
  defs = {}
  bbs = form_bbs(function)
  for bb in bbs:
    for inst in bb[0]:
      if 'dest' in inst:
        vars.add(inst['dest'])
        if inst['dest'] not in defs:
          defs[inst['dest']] = []
        defs[inst['dest']].append(bb[1])
  print(f'vars: {vars}', file=sys.stderr)
  print(f'defs: {defs}', file=sys.stderr)