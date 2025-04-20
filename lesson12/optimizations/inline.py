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
for inst in trace:
  trace_insts.append(inst)

json.dump(trace_insts, sys.stdout, indent=2, sort_keys=True)