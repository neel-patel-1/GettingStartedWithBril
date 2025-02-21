import json
import sys

vars = set()
prog = json.load(sys.stdin)
for function in prog['functions']:
  for inst in function['instrs']:
    if 'dest' in inst:
      vars.add(inst['dest'])
  print(f'vars: {vars}', file=sys.stderr)