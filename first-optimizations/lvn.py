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

counter = 0
seen_varse  = set()
def get_fresh_name():
  global counter
  counter += 1
  new_name = f'v{counter}'
  while new_name in seen_varse:
    counter += 1
    new_name = f'v{counter}'
  return new_name

def update_var_names(instr):
  if 'args' in instr:
    for arg in instr['args']:
      if arg not in seen_varse:
        seen_varse.add(arg)

expr_num_map = OrderedDict()
var2num = {}
alias_table = {}
def get_table_repr(expr):
  global expr_num_map, alias_table, var2num
  # Const
  if type(expr) == int or type(expr) == bool or type(expr) == str:
    if expr in expr_num_map:
      return (True, list(expr_num_map.keys()).index(expr)) # Literal we've seen
    else:
      return (False, (expr)) # New literal

  # Check if any aliases exist for this variable name already
  if 'args' in expr:
    new_args = []
    for arg in expr['args']:
      if arg in alias_table:
        new_args.append(alias_table[arg])
      else:
        new_args.append(arg)
    expr['args'] = new_args

  if 'op' in expr:
    if expr['op'] in ('add', 'sub', 'mul', 'div', 'lt', 'eq', 'gt', 'ge', 'le', 'and', 'or'):
      # arguments not in the table, make a placeholder entry
      if expr['args'][0] not in var2num:
        var2num[expr['args'][0]] = len(expr_num_map)
        expr_num_map[expr['args'][0]] = expr['args'][0]
      if expr['args'][1] not in var2num:
        var2num[expr['args'][1]] = len(expr_num_map)
        expr_num_map[expr['args'][1]] = expr['args'][1]

      arg1num = var2num[expr['args'][0]]
      arg2num = var2num[expr['args'][1]]

      # commutativity
      if expr['op'] in ('add', 'mul', 'and', 'or', 'eq'):
        arg1num, arg2num = min(arg1num, arg2num), max(arg1num, arg2num)

      # constant fold
      arg1expr = list(expr_num_map.keys())[arg1num]
      arg2expr = list(expr_num_map.keys())[arg2num]
      if (arg1expr[0] == 'const' and arg2expr[0] == 'const'):
        if expr['op'] in ('add'):
          key = ('const', 'int', arg1expr[2] + arg2expr[2])
        if expr['op'] in ('sub'):
          key = ('const', 'int', arg1expr[2] - arg2expr[2])
        if expr['op'] in ('mul'):
          key = ('const', 'int', arg1expr[2] * arg2expr[2])
        if expr['op'] in ('div'):
          key = ('const', 'int', arg1expr[2] // arg2expr[2])
        if expr['op'] in ('lt'):
          key = ('const', 'bool', arg1expr[2] < arg2expr[2])
        if expr['op'] in ('eq'):
          key = ('const', 'bool', arg1expr[2] == arg2expr[2])
        if expr['op'] in ('gt'):
          key = ('const', 'bool', arg1expr[2] > arg2expr[2])
        if expr['op'] in ('ge'):
          key = ('const', 'bool', arg1expr[2] >= arg2expr[2])
        if expr['op'] in ('le'):
          key = ('const', 'bool', arg1expr[2] <= arg2expr[2])
        if expr['op'] in ('and'):
          key = ('const', 'bool', arg1expr[2] and arg2expr[2])
        if expr['op'] in ('or'):
          key = ('const', 'bool', arg1expr[2] or arg2expr[2])
        if key in expr_num_map:
          var2num[expr['dest']] = list(expr_num_map.keys()).index(key)
          return (True, list(expr_num_map.keys()).index(key))
        else:
          var2num[expr['dest']] = len(expr_num_map)
          expr_num_map[key] = expr['dest']
          return (False, key)

      if (expr['op'], arg1num, arg2num) in expr_num_map: #already in the table
        var2num[expr['dest']] = list(expr_num_map.keys()).index((expr['op'], arg1num, arg2num))
        return (True, list(expr_num_map.keys()).index((expr['op'], arg1num, arg2num)))
      else: # not in the table
        var2num[expr['dest']] = len(expr_num_map)
        expr_num_map[(expr['op'], arg1num, arg2num)] = expr['dest']
        return (False, (expr['op'], arg1num, arg2num))

    if expr['op'] in ('id'):
      if expr['args'][0] in var2num: # the arg is in the current environment with a assigned table entry
        var2num[expr['dest']] = var2num[expr['args'][0]]
        return (True, var2num[expr['args'][0]])
      elif ('id', expr['args'][0]) in expr_num_map: # the arg not in the environment (live on entry), but someone else has already assigned to it
        var2num[expr['dest']] = list(expr_num_map.keys()).index(('id', expr['args'][0]))
        return (True, list(expr_num_map.keys()).index(('id', expr['args'][0])))
      else:
        var2num[expr['dest']] = len(expr_num_map)
        if expr['args'][0] in var2num: # the variable has been assigned in this bb
          expr_num_map[(expr['op'], expr['args'][0])] = expr['args'][0]
        else: # the variable is live on entry and we are responsible for supplying the value now
          expr_num_map[(expr['op'], expr['args'][0])] = expr['dest']

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
      return (False, expr['op'], expr)
    if expr['op'] in ('print'):
      return (False, expr['op'], expr)

    # TODO handle other ops

  # Label
  return (False, ['label', expr])

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
  function['instrs'] = []
  for bb in bbs:
    print(f'BB: {bb}', file=sys.stderr)
    expr_num_map.clear()
    var2num.clear()
    alias_table.clear()
    new_bb = []
    for instr in bb:
      # Check if we are re-assigning
      update_var_names(instr)
      if 'dest' in instr:
        if instr['dest'] in var2num:
          if instr['dest'] not in expr_num_map: # not a placeholder, then we have a re-assignment
            self_ref = False
            if 'args' in instr:
              for arg in instr['args']:
                if instr['dest'] == arg:
                  self_ref = True
            if not self_ref:
              renamed = True
              new_name = get_fresh_name()
              alias_table[instr['dest']] = new_name
              print(f'Var2Num: {var2num}', file=sys.stderr)
              instr['dest'] = new_name
            else: # remove the placeholder entry
              del var2num[instr['dest']]


      print(f'Instr: {instr}', file=sys.stderr)
      subst_expr = get_table_repr(instr)
      print(f'Expr: {subst_expr}', file=sys.stderr)
      if subst_expr[0] == True:
          new_source = list(expr_num_map.items())[subst_expr[1]][1]
          new_instr = {
            'args': [new_source],
            'dest': instr['dest'],
            'op': 'id',
            'type': instr['type']
          }
      elif subst_expr[1][0] == 'const':
        new_instr = {
          'dest': instr['dest'],
          'op': 'const',
          'type': instr['type'],
          'value': subst_expr[1][2]
        }
      else:
        new_instr = instr.copy()
        if 'op' in instr:
          if 'args' in instr:
            new_args = []
            for arg in instr['args']:
              if arg in var2num:
                if arg in alias_table:
                  arg = alias_table[arg]
                argnum = var2num[arg]
                argname = list(expr_num_map.items())[argnum][1]
                new_args.append(argname)
              else:
                new_args.append(arg)
            new_instr['args'] = new_args
      print(f'New Instr: {new_instr}', file=sys.stderr)
      new_bb.append(new_instr)
    function['instrs'].extend(new_bb)
print(json.dumps(prog, indent=2))