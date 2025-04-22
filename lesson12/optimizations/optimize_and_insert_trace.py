import json
import sys
from collections import OrderedDict
import os
DEBUG = True

def debug_print(message):
  if DEBUG:
    print(message, file=sys.stderr)


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

'''
for each file in traces/<function_name>_<start_inst_no>.json:
  trace_insts = read(file)
  opt_insts = optimize(trace_insts)
  for each inst in the trace:
    insert the instruction at the insertion point
'''
if len(sys.argv) < 2:
  print("Usage: python3 lvn.py <original_file> -- should have optimized traces in opt/traces/<original_file>/ ")
  sys.exit(1)

original_file = sys.argv[1]
if not os.path.exists(original_file):
  print(f"Error: File {original_file} does not exist.")
  sys.exit(1)


with open(original_file, 'r') as f:
  original_insts = json.load(f)

traces_dir = os.path.join("opt/traces", os.path.basename(original_file))
debug_print(f"Looking for traces in {traces_dir}")
trace_files = []
trace_files = [f for f in os.listdir(traces_dir) if os.path.isfile(os.path.join(traces_dir, f)) and f.endswith('.json')]
trace_files.sort(key=lambda x: (x.split('_')[0], -int(x.split('_')[1].split('.')[0])))
debug_print(f"Found {len(trace_files)} traces in {traces_dir}")

guard_trace_dir = os.path.join("guarded", "traces", os.path.basename(original_file))
debug_print(f"Emitting wrapped traces in {guard_trace_dir}")

for trace_file in trace_files:
  function_name, start_inst_no = trace_file.split('_')
  start_inst_no = int(start_inst_no.split('.')[0])
  with open(os.path.join(traces_dir, trace_file), 'r') as f:
    trace_insts = json.load(f)
    guards = get_guard_insts(trace_insts)
    for guard_inst in guards:
      cond_inst = {
        'op': guard_inst['op'],
        'args': guard_inst['args'],
        'dest': 'cond'
      }
      guard_inst = {
        'op': 'guard',
        'args': ['cond'],
        'labels': ['recover']
      }
      # find the safe location to put the cond and guard
      # Data structure to track which cond_inst args have been seen
      seen_args = set()

      # Iterate through the instructions to find the insertion point
      for i, inst in enumerate(trace_insts):
        if 'args' in inst:
          seen_args.update(inst['args'])
        # Check if all args of cond_inst are seen
        if all(arg in seen_args for arg in cond_inst['args']):
          # Insert cond_inst and guard_inst at this location
          trace_insts.insert(i, cond_inst)
          trace_insts.insert(i + 1, guard_inst)
          break

    commit_inst = { 'op': 'commit' }
    trace_insts.append(commit_inst)
    recover_inst = {'label': 'recover'}
    trace_insts.append(recover_inst)
    spec_inst = {'op': 'speculate'}
    trace_insts.insert(0, spec_inst)

    # remove inst if op is in inst and op is in ['jmp', 'br', 'label'] or if label is in inst
    trace_insts = [ inst for inst in trace_insts if 'op' in inst and inst['op'] not in ['jmp', 'br', 'label'] ]

    os.makedirs(guard_trace_dir, exist_ok=True)
    opt_trace_file = os.path.join(guard_trace_dir, trace_file)
    with open(opt_trace_file, 'w') as opt_f:
      json.dump(trace_insts, opt_f, indent=2)

# Load the original file

# for each guarded trace, grouped by function and in reverse order, insert the guarded trace into the location spepcified by the start_inst_no
guarded_trace_files = [f for f in os.listdir(guard_trace_dir) if os.path.isfile(os.path.join(guard_trace_dir, f)) and f.endswith('.json')]
guarded_trace_files.sort(key=lambda x: (x.split('_')[0], -int(x.split('_')[1].split('.')[0])))
for guarded_trace_file in guarded_trace_files:
  function_name, start_inst_no = guarded_trace_file.split('_')
  debug_print(f"Processing guarded trace file: {guarded_trace_file}")
  # Locate the function with the right name
  for func in original_insts['functions']:
    if func['name'] == function_name:
      # insert the guarded trace at the right location
      start_inst_no = int(start_inst_no.split('.')[0])
      debug_print(f"Found function {function_name} at index {start_inst_no}")
      # Read the guarded trace
      with open(os.path.join(guard_trace_dir, guarded_trace_file), 'r') as f:
        guarded_trace_insts = json.load(f)
        debug_print(f"Guarded trace instructions: {guarded_trace_insts}")
        # Insert the guarded trace at the right location
        func['instrs'] = func['instrs'][:start_inst_no] + guarded_trace_insts + func['instrs'][start_inst_no:]
        debug_print(f"Inserted {len(guarded_trace_insts)} instructions into function {function_name} at index {start_inst_no}")
      break



json.dump(original_insts, sys.stdout, indent=2, sort_keys=True)