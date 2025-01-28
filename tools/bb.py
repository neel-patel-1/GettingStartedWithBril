import json

TERMINATORS = 'br', 'jmp', 'ret'
file_path = 'bril/test/parse/positions.json'


# {'functions': [{'instrs': [{'dest': 'v0', 'op': 'const', 'type': 'int', 'value': 1}, {'dest': 'v1', 'op': 'const', 'type': 'int', 'value': 2}, {'args': ['v0', 'v1'], 'dest': 'v2', 'op': 'add', 'type': 'int'}, {'args': ['v2'], 'op': 'print'}], 'name': 'main'}]}

def form_bbs(data):
  functions = data['functions']
  for function in functions:
    instrs = function['instrs']
    bbs = []
    bb = []
    for instr in instrs:
      if 'op' in instr:
        bb.append(instr)
        # print(instr)
        if instr['op'] in TERMINATORS:
          # print(bb)
          bbs.append(bb)
          bb = []
    if bb:
      bbs.append(bb)
    return bbs


# to form edges, it may be useful to have a mapping from labels to blocks
# if the last instruction is a jump, get the
def form_cfg(bbs):
  cfg = {}
  for bb in bbs:
    last_inst = bb[-1]
    if(bbs.index(bb) + 1 == len(bbs)):
      cfg[bb] = []
    elif last_inst[op] == 'br':
      cfg[bb] = [bbs[bbs.index(bb) + 1], bbs[bb['args'][0]]]
    elif last_inst[op] == 'jmp':
      cfg[bb] = [bbs[bb['args'][0]]]


with open(file_path, 'r') as file:
  data = json.load(file)
  bbs = form_bbs(data)
  cfg = form_cfg(bbs)