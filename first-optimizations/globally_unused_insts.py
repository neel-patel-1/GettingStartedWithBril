import json
import sys

used = set()
passed_prog = []
deleted = True

def pass0(prog):
  global used
  for inst in prog:
    if 'args' in inst:
      for arg in inst['args']:
        used += arg

def pass1(prog):
  global deleted
  deleted = False
  for inst in prog:
    if 'dest' in inst:
      if inst['dest'] not in used:
        # get identifier of the inst to remove
        deleted = True
        continue
    passed_prog.append(inst)

prog = json.load(sys.stdin)
for func in prog['functions']:
  while deleted:
    pass0(func['instrs'])
    pass1(func['instrs'])