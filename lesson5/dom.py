import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}
insets = {}
outsets = {}
pred_map = {}
succ_map = {}
dom_map = {}

dom_map_changed = True

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class Tree:
    def __init__(self, root_value):
        self.root = TreeNode(root_value)

    def add_node(self, value, parent_value):
        parent_node = self.find_node(self.root, parent_value)
        if parent_node:
            parent_node.add_child(TreeNode(value))

    def find_node(self, current_node, value):
        if current_node.value == value:
            return current_node
        for child in current_node.children:
            found_node = self.find_node(child, value)
            if found_node:
                return found_node
        return None

    def traverse(self, node=None):
        if node is None:
            node = self.root
        print(node.value)
        for child in node.children:
            self.traverse(child)

    def display(self, node=None, level=0):
        if node is None:
            node = self.root
        print(' ' * level + str(node.value))
        for child in node.children:
            self.display(child, level + 2)

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

def initialize_bb_doms(bbs):
  global dom_map
  dom_map[bbs[0][1]] = set({bbs[0][1]})
  for bb in bbs[1:]:
    dom_map[bb[1]] = set(bb[1] for bb in bbs)

def get_bb_doms(bb, bb_list):
  global dom_map
  global pred_map
  print(f'Getting doms for {bb[1]}', file=sys.stderr)
  print(f'pred_map: {pred_map}', file=sys.stderr)
  if bb[1] in pred_map:
    preds = pred_map[bb[1]]
    doms = set(bb[1] for bb in bb_list)
    for pred in preds:
      if bb_list[pred][1] in dom_map:
        print(f'Intersecting Pred Doms from {bb_list[pred][1]}: {dom_map[bb_list[pred][1]]}', file=sys.stderr)
        doms.intersection_update(dom_map[bb_list[pred][1]])
    doms.add(bb[1])
    return doms
  else:
    return dom_map[bb[1]]

def gen_d_tree(bbs):
  global dom_map
  global succ_map
  dtree = Tree(bbs[0][1])
  for index, bb in enumerate(bbs):
    if index in succ_map:
      for b in succ_map[index]:
        if bb[1] in dom_map[b]:
          dtree.add_node(b, bb[1])
  return dtree



prog = json.load(sys.stdin)
for function in prog['functions']:
  bbs = form_bbs(function)
  print(f'bbs: {bbs}', file=sys.stderr)
  form_predecessor_map(bbs)
  form_successor_map(bbs)
  print(f'bbs: {bbs}', file=sys.stderr)
  print(f'pred_map: {pred_map}', file=sys.stderr)
  print(f'succ_map: {succ_map}', file=sys.stderr)

  initialize_bb_doms(bbs)
  print(f'dom_map: {dom_map}', file=sys.stderr)
  while dom_map_changed:
    dom_map_changed = False
    for bb in bbs:
      new_doms = get_bb_doms(bb, bbs)
      if new_doms != dom_map[bb[1]]:
        dom_map[bb[1]] = new_doms
        print(f'Updated doms for {bb[1]}: {dom_map[bb[1]]}', file=sys.stderr)
        dom_map_changed = True

  print(f'dom_map: {dom_map}', file=sys.stderr)
  gen_d_tree(bbs).display()
