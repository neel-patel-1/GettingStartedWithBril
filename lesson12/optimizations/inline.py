import json
import sys
import os

if len(sys.argv) < 3:
  print("Usage: python3 lvn.py <full_program> <trace>")
  sys.exit(1)

original_file = sys.argv[1]
trace_file = sys.argv[2]
if not os.path.exists(original_file):
  print(f"Error: File {original_file} does not exist.")
  sys.exit(1)

with open(original_file, 'r') as f:
  bril = json.load(f)
with open(trace_file, 'r') as f:
  trace = json.load(f)

functions = {}
for func in bril["functions"]:
  functions[func["name"]] = func

trace_insts = []
inlining = False
for index, inst in enumerate(trace):
  if 'op' in inst and inst['op'] == 'ret':
    inlining = False
    # TODO: handle recursion
    continue
  if 'op' in inst and inst['op'] == 'call':
    name = inst['funcs'][0]
    if name not in functions:
      print(f"Error: Function {name} not found in original file.")
      sys.exit(1)
    if 'args' in inst:
      args = inst['args']
      arg_map = {param["name"]: args[i] for i, param in enumerate(functions[name]["args"])}
    inlining = True
    # Rename local variables inside the function if they share names with variables before the function call
    local_vars = {instr["dest"] for instr in functions[name]["instrs"] if "dest" in instr}
    used_vars = {instr["dest"] for instr in trace_insts if "dest" in instr}
    rename_map = {}
    for var in local_vars:
      if var in used_vars:
        new_name = f"{var}_inlined_{index}"
        rename_map[var] = new_name


    # TODO: handle recursion
    continue
  if inlining:
    if 'args' in inst:
      inst['args'] = [ # rename arguments to the caller's variable names until they are reassigned
        arg_map[arg] if arg in arg_map and arg not in [i['dest'] for i in trace_insts if 'dest' in i] else arg
        for arg in inst['args']
      ]
    # Rename local variables inside the function if they share names with variables before the function call
    if "dest" in inst and inst["dest"] in rename_map:
      inst["dest"] = rename_map[inst["dest"]]
    if "args" in inst:
      inst["args"] = [rename_map[arg] if arg in rename_map else arg for arg in inst["args"]]

  trace_insts.append(inst)

json.dump(trace_insts, sys.stdout, indent=2, sort_keys=True)