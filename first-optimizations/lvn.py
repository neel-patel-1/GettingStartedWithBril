import json
import sys
from collections import OrderedDict

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

expr_num_map = OrderedDict()

def get_table_repr(expr):
  global expr_num_map, val_ctr
  # Const
  if type(expr) == int or type(expr) == bool or type(expr) == str:
    if expr in expr_num_map:
      return (True, list(expr_num_map.keys()).index(expr)) # Literal we've seen
    else:
      return (False, (expr)) # New literal

  # Inst
  if 'op' in expr:
    if expr['op'] in ('add', 'sub', 'mul', 'div', 'lt', 'eq', 'gt', 'ge', 'le', 'and', 'or'):
      return (expr['op'], get_table_repr(expr['args'][0]), get_table_repr(expr['args'][0]))
    if expr['op'] in ('id'):
      if (expr['op'], expr['args'][0]) in expr_num_map:
        return (True, list(expr_num_map.keys()).index(expr))
      else:
        expr_num_map[(expr['op'], expr['args'][0])] = expr['dest']
        return (False, (expr['op'], expr['args'][0]))
    if expr['op'] in ('const'):
      if (expr['op'], expr['type'], expr['value']) in expr_num_map:
        return (True, list(expr_num_map.keys()).index(expr))
      else:
        expr_num_map[(expr['op'], expr['type'], expr['value'])] = expr['dest']
        return (False, (expr['op'], expr['type'], expr['value']))

    if expr['op'] in ('jmp'):
      return (expr['op'], expr)
    if expr['op'] in ('print'):
      return (expr['op'], expr)
    # TODO handle other ops

  # Label
  if 'label' in expr:
    return (expr['label'], expr)

def new_instr(expr):
  if(expr[0] == 'id'):
    source = expr_num_map[expr[1]]
    return {'args': []}


prog = json.load(sys.stdin)
for function in prog['functions']:
  bbinfo = form_bbs(function)
  bbs = bbinfo[0]
  for bb in bbs:
    expr_num_map.clear()
    for instr in bb:
      print(f'Instr: {instr}')
      subst_expr = get_table_repr(instr)
      print(f'Expr: {subst_expr}')

# print(json.dumps(prog, indent=2))
