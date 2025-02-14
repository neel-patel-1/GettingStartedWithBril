import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}
insets = {}
outsets = {}
pred_map = {}
succ_map = {}

counter = 0
def get_fresh_bb_name():
  global counter
  counter += 1
  new_name = f'b{counter}'
  return new_name

def form_bbs(function):
  num_bbs = 0
  bbs = []
  instrs = function['instrs']
  bb = []
  bb_label = 'Entry'
  for instr in instrs:
    bb.append(instr)
    if 'label' in instr and len(bb) == 1:
      bb_label = instr['label']
    if 'op' in instr:
      if instr['op'] in TERMINATORS:
        if bb_label == None:
          bb_label = get_fresh_bb_name()
        bbs.append((bb, bb_label,None,None))
        bb = []
        num_bbs += 1
        bb_label = None
    if 'label' in instr and len(bb) > 1:
      if bb_label == None:
        bb_label = get_fresh_bb_name()
      bb = bb[:-1]
      bbs.append((bb, bb_label,None,None))
      bb = [instr]
      bb_label = instr['label']
      num_bbs += 1
  if bb:
    if bb_label == None:
      bb_label = get_fresh_bb_name()
    bbs.append((bb, bb_label,None,None))
    num_bbs += 1
  return (bbs)

def form_predecessor_map(bbs):
  global pred_map
  for index, bb in enumerate(bbs):
    print(f'bb: {bb[1]}', file=sys.stderr)
    if 'op' in bb[0][-1]:
      if bb[0][-1]['op'] in TERMINATORS:
        if 'labels' in bb[0][-1]:
          for label in bb[0][-1]['labels']:
            if label in pred_map:
              pred_map[label].append(index)
            else:
              pred_map[label] = [index]
      elif index < len(bbs) - 1:
        if bbs[index + 1][1] in pred_map:
          pred_map[bbs[index + 1][1]].append(index)
        else:
          pred_map[bbs[index + 1][1]] = [index]
    else: # empty bb
      if index < len(bbs) - 1:
        if bbs[index + 1][1] in pred_map:
          pred_map[bbs[index + 1][1]].append(index)
        else:
          pred_map[bbs[index + 1][1]] = [index]

def form_successor_map(bbs):
  global succ_map
  for index, bb in enumerate(bbs):
    if 'op' in bb[0][-1]:
      if bb[0][-1]['op'] in TERMINATORS:
        if 'labels' in bb[0][-1]:
          for label in bb[0][-1]['labels']:
            if index in succ_map:
              succ_map[index].append(label)
            else:
              succ_map[index] = [label]
      elif index < len(bbs) - 1:
        if index in succ_map:
          succ_map[index].append(bbs[index + 1][1])
        else:
          succ_map[index] = [bbs[index + 1][1]]
    else: # empty bb
      if index < len(bbs) - 1:
        if index in succ_map:
          succ_map[index].append(bbs[index + 1][1])
        else:
          succ_map[index] = [bbs[index + 1][1]]

def transfer(bb, inset):
  outset = inset.copy()
  for instr in bb[0]:
    if 'op' in instr:
      print(f'instr: {instr}', file=sys.stderr)
      if instr['op'] in ('add', 'mul', 'and', 'or', 'eq'):
        if instr['args'][0] in inset and instr['args'][1] in inset and inset[instr['args'][0]] != None and inset[instr['args'][1]] != None:
          val1 = inset[instr['args'][0]]
          val2 = inset[instr['args'][1]]
          if instr['op'] == 'add':
            result = val1 + val2
          elif instr['op'] == 'mul':
            result = val1 * val2
          elif instr['op'] == 'and':
            result = val1 and val2
          elif instr['op'] == 'or':
            result = val1 or val2
          elif instr['op'] == 'eq':
            result = val1 == val2
          outset[instr['dest']] = result
      if instr['op'] in 'const':
        outset[instr['dest']] = instr['value']
        print(f'outset: {outset}', file=sys.stderr)
      if instr['op'] in 'id':
        if instr['args'][0] in inset and inset[instr['args'][0]] != None:
          outset[instr['dest']] = inset[instr['args'][0]]
  return outset

def create_inset(name, bb_list):
  global pred_map
  inset = {}
  if name in pred_map:
    print(f'PredMap {pred_map}', file=sys.stderr)
    for pred in pred_map[name]:
      pred_id = bb_list[pred][1]
      if pred_id in outsets:
        print(f'outset: {outsets[pred_id]}', file=sys.stderr)
        for key, value in outsets[pred_id].items():
          if key in inset and inset[key] != value:
            inset[key] = None
          else:
            inset[key] = value
  return inset

def transform_block(block, inset):
  new_block = []
  for instr in block[0]:
    if 'op' in instr:
      if 'dest' in instr and 'args' in instr:
        print(f'inset: {inset}', file=sys.stderr)
        if instr['dest'] in inset and inset[instr['dest']] != None:
          new_instr = {'op': 'const', 'dest': instr['dest'], 'value': inset[instr['dest']]}
          new_block.append(new_instr)
        elif instr['args'][0] in inset and instr['args'][1] in inset and inset[instr['args'][0]] != None and inset[instr['args'][1]] != None:
          val1 = inset[instr['args'][0]]
          val2 = inset[instr['args'][1]]
          if instr['op'] == 'add':
            result = val1 + val2
            new_instr = {'op': 'const', 'dest': instr['dest'], 'value': result}
            new_block.append(new_instr)
          elif instr['op'] == 'mul':
            result = val1 * val2
            new_instr = {'op': 'const', 'dest': instr['dest'], 'value': result}
            new_block.append(new_instr)
          elif instr['op'] == 'and':
            result = val1 and val2
            new_instr = {'op': 'const', 'dest': instr['dest'], 'value': result}
            new_block.append(new_instr)
          elif instr['op'] == 'or':
            result = val1 or val2
            new_instr = {'op': 'const', 'dest': instr['dest'], 'value': result}
            new_block.append(new_instr)
          elif instr['op'] == 'eq':
            result = val1 == val2
            new_instr = {'op': 'const', 'dest': instr['dest'], 'value': result}
            new_block.append(new_instr)
      else:
        new_block.append(instr)
    else:
      new_block.append(instr)
  return (new_block, block[1],block[2],block[3])
name2id = {}

prog = json.load(sys.stdin)
for function in prog['functions']:
  outsets.clear()
  insets.clear()
  use_defs.clear()
  pred_map.clear()
  succ_map.clear()
  bbs = form_bbs(function)
  form_predecessor_map(bbs)
  print(f'Predecessor map: {pred_map}', file=sys.stderr)
  form_successor_map(bbs)
  print(f'Successor map: {succ_map}', file=sys.stderr)

  bbq = queue.Queue()
  in_queue = set()  # Set to keep track of entries in the queue
  for index, bb in enumerate(bbs):
    bbq.put(index)
    in_queue.add(index)
    name2id[bb[1]] = index

  while not bbq.empty():
    bbid = bbq.get()
    in_queue.remove(bbid)  # Remove from in_queue when dequeued
    bb = bbs[bbid]
    inset = create_inset(bb[1], bbs)
    if bb[1] in outsets:
      outset = outsets[bb[1]]
    else:
      outset = {}
    print(f'Running transfer on {bb[1]} with inset {inset}', file=sys.stderr)
    new_outset = transfer(bb, inset)
    if new_outset != outset or bb[1] not in insets:
      print(f'Updating outset for {bb[1]} from {inset} to {new_outset}', file=sys.stderr)
      outsets[bb[1]] = new_outset
      if bb[1] in succ_map:
        for succ in succ_map[bb[1]]:
          if succ not in in_queue:  # Add to queue only if not already in there
            print(f'Readding {bbs[succ][1]} due to {bb[1]} who\'s outset is now {new_outset}', file=sys.stderr)
            bbq.put(succ)
            in_queue.add(succ)


# propogate the constants through the code
  new_bbs = []
  for index, bb in enumerate(bbs):
    inset = create_inset(bb[1], bbs)
    print(f'bb: {bb[1]} inset: {inset}', file=sys.stderr)
    print(f'old_bb: {bb[0]}', file=sys.stderr)
    new_bb = transform_block(bb, inset)
    print(f'new_bb: {new_bb}', file=sys.stderr)
    new_bbs.append(new_bb)

  function['instrs'] = []
  for bb in new_bbs:
    function['instrs'] += bb[0]

print(json.dumps(prog))

