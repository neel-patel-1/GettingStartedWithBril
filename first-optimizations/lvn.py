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
env_name_map = {}
val_num = 0
val_ctr = 0

def get_env_mapping(varname):
  global env_name_map
  if varname in env_name_map:
    return env_name_map[varname]
  else:
    return None

def get_table_repr(expr):
  global expr_num_map
  # Const
  if type(expr) == int or type(expr) == bool:
    if expr in expr_num_map:
      return expr_num_map[expr] # Literal we've seen
    else:
      return (expr) # New literal

  # Varname
  if type(expr) == str:
    if expr in expr_num_map:
      return expr_num_map[expr]
    else:
      return (expr)

  # Inst
  if 'op' in expr:
    if expr['op'] in ('add', 'sub', 'mul', 'div', 'lt', 'eq', 'gt', 'ge', 'le', 'and', 'or'):
      return (expr['op'], get_table_repr(expr['args'][0]), get_table_repr(expr['args'][0]))
    if expr['op'] in ('id'):
      val_num = get_env_mapping(expr['args'][0])
      if val_num is None:
        global val_ctr
        # create a new "value" that maps to a new number
        expr_num_map[(expr['op'], expr['args'][0])] = val_ctr
        # add an env mapping for this variable
        env_name_map[expr['dest']] = val_ctr
        val_ctr += 1
        return (expr['op'], (expr['op'], expr['args'][0]))
      else:
        env_name_map[expr['dest']] = val_num
        return (expr['op'], val_num)
    if expr['op'] in ('const'):
      return (expr['dest'], (expr['op'],get_table_repr(expr['value'])))
    if expr['op'] in ('jmp'):
      return (expr['op'], expr)
    if expr['op'] in ('print'):
      return (expr['op'], expr)
    # TODO handle other ops

  # Label
  if 'label' in expr:
    return (expr['label'], expr)


prog = json.load(sys.stdin)
for function in prog['functions']:
  bbinfo = form_bbs(function)
  bbs = bbinfo[0]
  for bb in bbs:
    expr_num_map.clear()
    for instr in bb:
      print(f'Instr: {instr}')
      repr_info = get_table_repr(instr)
      print(f'Expr: {repr_info}')

# print(json.dumps(prog, indent=2))
