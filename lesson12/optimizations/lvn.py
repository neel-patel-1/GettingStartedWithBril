import json
import sys
from collections import OrderedDict
import os

'''
goes through insts, checks for control flow to determining the guards to insert
'''

seen_conditions = {}

def opt_insts(trace_insts):
  conditions_to_guard_on = []
  expecting_label = False
  for inst in trace_insts:
    print(f"Processing instruction: {inst}")
    if expecting_label:
      if 'label' not in inst:
        raise ValueError("Expected to see a label after executing a branch, got: %s" % inst)
      else:
        condition_to_guard_on = condition
        if true_label == inst['label']:
          condition_to_guard_on['satisfy'] = True
        elif false_label == inst['label']:
          condition_to_guard_on['satisfy'] = False
        conditions_to_guard_on.append(condition_to_guard_on)
        print(f"Guard condition: {condition_to_guard_on}")
        expecting_label = False
    if 'op' in inst:
      if inst['op'] in ['eq', 'ne', 'lt', 'le', 'gt', 'ge']:
        condition = { 'op': inst['op'], 'args': inst['args'] }
        seen_conditions[inst['dest']] = condition
        print(f"Seen condition: {condition}")
      if inst['op'] == 'br':
        cond_id = inst['args'][0]
        if cond_id not in seen_conditions:
            raise RuntimeError("Branching on a never-before-seen condition: %s" % cond_id)
        condition = seen_conditions[cond_id]
        print(f"Condition for branch: {condition}")
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
trace_files = []
traces_dir = "traces"
if os.path.exists(traces_dir) and os.path.isdir(traces_dir):
  trace_files = [f for f in os.listdir(traces_dir) if os.path.isfile(os.path.join(traces_dir, f)) and f.endswith('.json')]
  trace_files.sort(key=lambda x: (x.split('_')[0], -int(x.split('_')[1].split('.')[0])))
  print(f"Found {len(trace_files)} traces in {traces_dir}")

  # read in and listify the files and emit the guard instructions produced
  all_instructions = []
  for trace_file in trace_files:
    with open(os.path.join(traces_dir, trace_file), 'r') as f:
      trace_insts = json.load(f)
      guard_insts = opt_insts(trace_insts)
      print(f"Guard instructions for {trace_file}:")
      for guard_inst in guard_insts:
        print(guard_inst)
