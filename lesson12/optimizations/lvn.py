import json
import sys
from collections import OrderedDict
import os
DEBUG = False

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
    debug_print(f"Processing instruction: {inst}")
    if expecting_label:
      if 'label' not in inst:
        raise ValueError("Expected to see a label after executing a branch, got: %s" % inst)
      else:
        condition_to_guard_on = condition
        if false_label == inst['label']:
          condition_to_guard_on ['op'] = opposite_ops[guard_inst['op']]
        elif not true_label == inst['label']:
          raise ValueError("Expected to see a label from the last branch instruction, got: %s" % inst['label'])
        debug_print(f"Condition to guard on: {condition_to_guard_on}")
        conditions_to_guard_on.append(condition_to_guard_on)
        expecting_label = False
    if 'op' in inst:
      if inst['op'] in ['eq', 'ne', 'lt', 'le', 'gt', 'ge']:
        condition = { 'op': inst['op'], 'args': inst['args'] }
        seen_conditions[inst['dest']] = condition
        debug_print(f"Seen condition: {condition}")
      if inst['op'] == 'br':
        cond_id = inst['args'][0]
        if cond_id not in seen_conditions:
            raise RuntimeError("Branching on a never-before-seen condition: %s" % cond_id)
        condition = seen_conditions[cond_id]
        debug_print(f"Condition for branch: {condition}")
        true_label = inst['labels'][0]
        false_label = inst['labels'][1]
        expecting_label = True
  return conditions_to_guard_on

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

for trace_file in trace_files:
  function_name, start_inst_no = trace_file.split('_')
  start_inst_no = int(start_inst_no.split('.')[0])
  with open(os.path.join(traces_dir, trace_file), 'r') as f:
    trace_insts = json.load(f)
    guard_insts = get_guard_insts(trace_insts)
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

with open(opt_file, 'w') as f:
  json.dump(original_insts, f, indent=2)
exit(0)
trace_files = []
traces_dir = "traces"
if os.path.exists(traces_dir) and os.path.isdir(traces_dir):
  trace_files = [f for f in os.listdir(traces_dir) if os.path.isfile(os.path.join(traces_dir, f)) and f.endswith('.json')]
  trace_files.sort(key=lambda x: (x.split('_')[0], -int(x.split('_')[1].split('.')[0])))
  debug_print(f"Found {len(trace_files)} traces in {traces_dir}")

  # read in and listify the files and emit the guard instructions produced
  all_instructions = []
  for trace_file in trace_files:
    with open(os.path.join(traces_dir, trace_file), 'r') as f:
      trace_insts = json.load(f)
      guard_insts = get_guard_insts(trace_insts)
      debug_print(f"Guard instructions for {trace_file}:")
      prepend_inst = {
        'op': 'speculate'
      }
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
      prepend_inst = {
        'label': 'recover',
      }
      prepend_insts.append(prepend_inst)
      debug_print(f"Prepend instructions for {trace_file}:")
      for inst in prepend_insts:
        debug_print(inst)
      # insert the instructions at the offset of the function specified by the trace file <function_name>_<start_inst_no>.json