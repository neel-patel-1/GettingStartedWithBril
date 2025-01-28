import json


file_path = 'bril/test/parse/add.json'

with open(file_path, 'r') as file:
  data = json.load(file)

# {'functions': [{'instrs': [{'dest': 'v0', 'op': 'const', 'type': 'int', 'value': 1}, {'dest': 'v1', 'op': 'const', 'type': 'int', 'value': 2}, {'args': ['v0', 'v1'], 'dest': 'v2', 'op': 'add', 'type': 'int'}, {'args': ['v2'], 'op': 'print'}], 'name': 'main'}]}

functions = data['functions']
for function in functions:
  instrs = function['instrs']
  bb = []
  for instr in instrs:
    if instr['op'] == 'jmp':
      bb.append(instr['label'])


print(data)