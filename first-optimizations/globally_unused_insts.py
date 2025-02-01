import json
import sys

used = set()
passed_func = []
deleted = True
num_deleted = 0

def pass0(prog):
  global used
  for inst in prog:
    if 'args' in inst:
      for arg in inst['args']:
        used.add(arg)
    if 'op' in inst:
      if inst['op'] == 'print':
        for arg in inst['args']:
          used.add(arg)

def pass1(prog):
  global deleted, passed_func
  global num_deleted
  for inst in prog:

    if 'dest' in inst:
      if inst['dest'] not in used:
        # get identifier of the inst to remove
        deleted = True
        num_deleted += 1
        continue
    passed_func.append(inst)

prog = json.load(sys.stdin)

# globally unused
for func in prog['functions']:
  deleted = True
  while deleted:
    deleted = False # if deleted gets set to False before the condition is checked, then the pass can only run once
    pass0(func['instrs']) # after each pass, we need to update the func
    pass1(func['instrs'])
    func['instrs'] = passed_func
    passed_func = []
    used.clear()

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

# locally killed
for function in prog['functions']:
  bbinfo = form_bbs(function)
  bbs = bbinfo[0]

print(json.dumps(prog, indent=2))