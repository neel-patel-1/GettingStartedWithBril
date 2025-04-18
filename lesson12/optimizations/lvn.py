import json
import sys
from collections import OrderedDict

'''
goes through insts, checks for control flow to determining the guards to insert
'''

seen_conditions = {}

def opt_insts(trace_insts):
  for inst in trace_insts:
    if 'cond' in inst:
      condition = { 'op': inst['op'], 'args': inst['args'] }
      seen_conditions[inst['dest']] = condition
    if 'br' in inst:
      cond_id = inst['args'][0]
      if cond_id not in seen_conditions:
          raise RuntimeError("Branching on a never-before-seen condition")
      condition = seen_conditions[cond_id]
      true_label = inst.labels[0]
      false_label = inst.labels[1]
      expecting_label = True
    if expecting_label:
      if 'label' not in inst:
        raise ValueError("Expected to see a label after executing a branch")
      else:
        condition_to_guard_on = condition
        if true_label == inst['label']:
          condition_to_guard_on['satisfy'] = True
        elif false_label == inst['label']:
          condition_to_guard_on['satisfy'] = False




'''
for each file in traces/<function_name>_<start_inst_no>.json:
  trace_insts = read(file)
  opt_insts = optimize(trace_insts)
  for each inst in the trace:
    insert the instruction at the insertion point

'''