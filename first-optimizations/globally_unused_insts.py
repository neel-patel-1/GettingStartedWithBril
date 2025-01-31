import json
import sys

used = set()
passed_func = []
deleted = True

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
  for inst in prog:

    if 'dest' in inst:
      if inst['dest'] not in used:
        # get identifier of the inst to remove
        deleted = True
        continue
    passed_func.append(inst)

prog = json.load(sys.stdin)
passed_prog = {'functions': []}
for func in prog['functions']:
  deleted = True
  while deleted:
    pass0(func['instrs'])
    pass1(func['instrs'])
    used.clear()
    deleted = False
  passed_prog['functions'].append({'name': func['name'], 'instrs': passed_func})
  if 'type' in func:
    passed_prog['functions'][-1]['type'] = func['type']
  if 'args' in func:
    passed_prog['functions'][-1]['args'] = func['args']
  passed_func = []

print(json.dumps(passed_prog, indent=2))