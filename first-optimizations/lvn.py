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
var2num = {}
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
      if expr['args'][0] in var2num:
        var2num[expr['dest']] = var2num[expr['args'][0]]
        return (True, var2num[expr['args'][0]])
      else:
        var2num[expr['dest']] = len(expr_num_map)
        expr_num_map[(expr['op'], expr['args'][0])] = expr['args'][0]

        return (False, (expr['op'], expr['args'][0]))
    if expr['op'] in ('const'):
        key = (expr['op'], expr['type'], expr['value'])
        dest = expr['dest']
        if key in expr_num_map:
          var2num[dest] = list(expr_num_map.keys()).index(key)
          return (True, list(expr_num_map.keys()).index(key))
        else:
          var2num[dest] = len(expr_num_map)
          expr_num_map[key] = dest
          return (False, key)
    if expr['op'] in ('jmp'):
      return (expr['op'], expr)
    if expr['op'] in ('print'):
      return (expr['op'], expr)
    # TODO handle other ops

  # Label
  if 'label' in expr:
    return (expr['label'], expr)

def new_instr(old_inst, expr):
  if(expr[0] == False):
    new_inst = old_inst
  else:
    if old_inst['op'] in ('const'):
      # this inst can be deleted
      return None
    if old_inst['op'] in ('id'):
      mapped_expr = list(expr_num_map.keys())[expr[1]]


prog = json.load(sys.stdin)
for function in prog['functions']:
  bbinfo = form_bbs(function)
  bbs = bbinfo[0]
  for bb in bbs:
    expr_num_map.clear()
    var2num.clear()
    new_bb = []
    for instr in bb:
      print(f'Instr: {instr}')
      subst_expr = get_table_repr(instr)
      print(f'Expr: {subst_expr}')
      if subst_expr[0] == True:
        if instr['op'] == 'id':
          new_source = list(expr_num_map.keys())[subst_expr[1]][1]
          new_instr = {
            'args': [list(expr_num_map.keys())[subst_expr[1]][1]],
            'dest': instr['dest'],
            'op': 'id',
            'type': instr['type']
          }
      else:
        new_instr = instr.copy()
      print(f'New Instr: {new_instr}')

# print(json.dumps(prog, indent=2))
