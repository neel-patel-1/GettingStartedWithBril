import json
import sys
from collections import OrderedDict
import os
DEBUG = True

def debug_print(message):
  if DEBUG:
    print(message)


seen_conditions = {}
opposite_ops = {
  'eq': 'ne',
  'ne': 'eq',
  'lt': 'ge',
  'le': 'gt',
  'gt': 'le',
  'ge': 'lt'
}

'''
goes through insts, checks for control flow to determining the guards to insert
'''
def get_guard_insts(trace_insts):
  conditions_to_guard_on = []
  expecting_label = False
  for inst in trace_insts:
    # debug_print(f"Processing instruction: {inst}")
    if expecting_label:
      if 'label' not in inst:
        raise ValueError("Expected to see a label after executing a branch, got: %s" % inst)
      else:
        condition_to_guard_on = condition
        if false_label == inst['label']:
          condition_to_guard_on ['op'] = opposite_ops[guard_inst['op']]
        elif not true_label == inst['label']:
          raise ValueError("Expected to see a label from the last branch instruction, got: %s" % inst['label'])
        debug_print(f"GuardGen: Condition to guard on: {condition_to_guard_on}")
        conditions_to_guard_on.append(condition_to_guard_on)
        expecting_label = False
    if 'op' in inst:
      if inst['op'] in ['eq', 'ne', 'lt', 'le', 'gt', 'ge']:
        condition = { 'op': inst['op'], 'args': inst['args'] }
        seen_conditions[inst['dest']] = condition
        # debug_print(f"Seen condition: {condition}")
      if inst['op'] == 'br':
        cond_id = inst['args'][0]
        if cond_id not in seen_conditions:
            raise RuntimeError("Branching on a never-before-seen condition: %s" % cond_id)
        condition = seen_conditions[cond_id]
        # debug_print(f"Condition for branch: {condition}")
        true_label = inst['labels'][0]
        false_label = inst['labels'][1]
        expecting_label = True
  return conditions_to_guard_on

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

def lvn(trace_insts):
  optimized_insts = []
  for instr in trace_insts:
    # debug_print(f"LVN: Processing instruction: {instr}")
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
            debug_print(f"Renaming {instr['dest']} to a new name")
            new_name = get_fresh_name()
            alias_table[instr['dest']] = new_name
            instr['dest'] = new_name
          else: # remove the placeholder entry
            del var2num[instr['dest']]

    subst_expr = get_table_repr(instr)
    if subst_expr[0] == True:
        new_source = list(expr_num_map.items())[subst_expr[1]][1]
        new_instr = instr.copy()
        new_instr['dest'] = instr['dest']
        new_instr['args'] = [new_source]
        new_instr['op'] = 'id'

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
    debug_print(f"LVN: New instruction: {new_instr}")
    optimized_insts.append(new_instr)
  print(f'Optimized Instructions: {optimized_insts}', file=sys.stderr)
  return optimized_insts

marked = []
found_killed = True
def mark_locally_killed(bb):
  candidates = {}
  instr_index = 0
  for instr in bb:
    if 'args' in instr:
      for arg in instr['args']:
        if arg in candidates:
          # print(f"Removed Candidate {arg} at {candidates[arg]}")
          del candidates[arg]
    if 'dest' in instr:
      if instr['dest'] in candidates:
        marked.append(candidates[instr['dest']])
        # print(f"Marked {instr['dest']} at {candidates[instr['dest']]}")
      if not instr['op'] == 'call' and not instr['op'] == 'print':
        candidates[instr['dest']] = instr_index
        # print(f"Added Candidate {instr['dest']} at {instr_index}")

    instr_index += 1

def remove_locally_killed(bb):
  global found_killed, marked
  passed_bb = []
  instr_index = 0
  for instr in bb:
    if instr_index not in marked:
      passed_bb.append(instr)
    else:
      found_killed = True
      # print(f"Deleted {instr['dest']} at {instr_index}")
    instr_index += 1
  return passed_bb

def dce(bb):
  global marked, found_killed
  marked = []
  found_killed = True
  while found_killed:
    found_killed = False
    mark_locally_killed(bb)
    bb = remove_locally_killed(bb)
  return bb

def opt_insts(trace_insts):
  lvn_insts = lvn(trace_insts)
  dce_insts = dce(lvn_insts)
  print(f'LVN Instructions: {lvn_insts}', file=sys.stderr)
  print(f'DCE Instructions: {dce_insts}', file=sys.stderr)
  return dce_insts

'''
for each file in traces/<function_name>_<start_inst_no>.json:
  trace_insts = read(file)
  opt_insts = optimize(trace_insts)
  for each inst in the trace:
    insert the instruction at the insertion point
'''
if len(sys.argv) < 3:
  print("Usage: python3 lvn.py <original_file> <opt_file>")
  sys.exit(1)

original_file = sys.argv[1]
opt_file = sys.argv[2]
if not os.path.exists(original_file):
  print(f"Error: File {original_file} does not exist.")
  sys.exit(1)


with open(original_file, 'r') as f:
  original_insts = json.load(f)

traces_dir = os.path.join("traces", os.path.basename(original_file))
debug_print(f"Looking for traces in {traces_dir}")
trace_files = []
trace_files = [f for f in os.listdir(traces_dir) if os.path.isfile(os.path.join(traces_dir, f)) and f.endswith('.json')]
trace_files.sort(key=lambda x: (x.split('_')[0], -int(x.split('_')[1].split('.')[0])))
debug_print(f"Found {len(trace_files)} traces in {traces_dir}")

opt_trace_dir = os.path.join("opt", "traces", os.path.basename(original_file))
debug_print(f"Emitting optimized traces in {opt_trace_dir}")

for trace_file in trace_files:
  function_name, start_inst_no = trace_file.split('_')
  start_inst_no = int(start_inst_no.split('.')[0])
  with open(os.path.join(traces_dir, trace_file), 'r') as f:
    trace_insts = json.load(f)
    optimized_insts = opt_insts(trace_insts)
    guard_insts = get_guard_insts(optimized_insts)
    prepend_inst = {'op': 'speculate'}
    prepend_insts = [prepend_inst]
    for guard_inst in guard_insts:
      prepend_inst = {
        'op': guard_inst['op'],
        'args': guard_inst['args'],
        'dest': 'cond'
      }
      prepend_insts.append(prepend_inst)
      prepend_inst = {
        'op': 'guard',
        'args': ['cond'],
        'labels': ['recover']
      }
      prepend_insts.append(prepend_inst)
    prepend_insts += trace_insts
    prepend_inst = {'label': 'recover'}
    prepend_insts.append(prepend_inst)

    os.makedirs(opt_trace_dir, exist_ok=True)
    opt_trace_file = os.path.join(opt_trace_dir, trace_file)
    with open(opt_trace_file, 'w') as opt_f:
      json.dump(prepend_insts, opt_f, indent=2)

with open(opt_file, 'w') as f:
  json.dump(original_insts, f, indent=2)