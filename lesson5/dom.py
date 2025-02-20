import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
use_defs = {}
insets = {}
outsets = {}
pred_map = {}
succ_map = {}
succ_map_2 = {}
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
        print(' ' * level + str(node.value), file=sys.stderr)
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
  bb_label = instrs[0]['label'] if 'label' in instrs[0] else 'Entry'
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
    # print(f'bb: {bb[1]}', file=sys.stderr)
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
  # print(f'Getting doms for {bb[1]}', file=sys.stderr)
  # print(f'pred_map: {pred_map}', file=sys.stderr)
  if bb[1] in pred_map:
    preds = pred_map[bb[1]]
    doms = set(bb[1] for bb in bb_list)
    for pred in preds:
      if bb_list[pred][1] in dom_map:
        # print(f'Intersecting Pred Doms from {bb_list[pred][1]}: {dom_map[bb_list[pred][1]]}', file=sys.stderr)
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

def gen_cfg(bbs):
  global pred_map
  global succ_map
  cfg = Tree(bbs[0][1])
  for index, bb in enumerate(bbs):
    if index in succ_map:
      for b in succ_map[index]:
        cfg.add_node(b, bb[1])
  return cfg

def get_all_paths(to, start):
  global succ_map_2
  paths = set()
  # collect every path from entry to 'to'
  # a path is terminated once a repeat is hit
  # or when 'to' is reached
  # a path is only added if it ends in 'to
  q = queue.Queue()
  q.put([start])
  while not q.empty():
    path = q.get()
    if path[-1] == to:
      paths.add(tuple(path))
    else:
      if path[-1] in succ_map_2:
        for succ in succ_map_2[path[-1]]:
          if succ not in path:
            q.put(path + [succ])
  return paths

def check_node(doms, node):
  all_good = True
  if dom_map[node] != doms:
    all_good = False
    return all_good
  for child in tree.find_node(tree.root, node).children:
    with_child = doms.copy()
    with_child.add(child.value)
    all_good = all_good and check_node(with_child, child.value)
  return all_good

def dom_frontier(bb, tree):
  global dom_map
  global succ_map
  dom_frontier = set()
  # search down the tree in a breadth-first manner stopping threads that see the same node again -> {child_set}
  child_set = set()
  q = queue.Queue()
  q.put(bb[1])
  while not q.empty():
    node = q.get()
    for child in tree.find_node(tree.root, node).children:
      if child.value not in child_set:
        child_set.add(child.value)
        q.put(child.value)

  # for each child in child_set, if bb is not in the dom_map of child, add child to dom_frontier
  for child in child_set:
    if bb[1] not in dom_map[child]:
      dom_frontier.add(child)
  return dom_frontier

prog = json.load(sys.stdin)
for function in prog['functions']:
  dom_map_changed = True
  dom_map.clear()
  pred_map.clear()
  succ_map.clear()
  succ_map_2.clear()
  bbs = []
  bbs = form_bbs(function)
  # print(f'bbs: {bbs}', file=sys.stderr)
  form_predecessor_map(bbs)
  form_successor_map(bbs)
  # print(f'bbs: {bbs}', file=sys.stderr)
  # print(f'pred_map: {pred_map}', file=sys.stderr)
  # print(f'succ_map: {succ_map}', file=sys.stderr)

  initialize_bb_doms(bbs)
  # print(f'dom_map: {dom_map}', file=sys.stderr)
  while dom_map_changed:
    dom_map_changed = False
    print(f'dom_map: {dom_map}', file=sys.stderr)
    for bb in bbs[1:]:
      new_doms = get_bb_doms(bb, bbs)
      if new_doms != dom_map[bb[1]]:
        dom_map[bb[1]] = new_doms
        print(f'Updated doms for {bb[1]}: {dom_map[bb[1]]}', file=sys.stderr)
        dom_map_changed = True

  # print(f'dom_map: {dom_map}', file=sys.stderr)
  tree = gen_d_tree(bbs)
  tree.display()

  cfg = gen_cfg(bbs)
  for bb in bbs:
    frontier = dom_frontier(bb, cfg)
    # print(f'Dom Frontier for {bb[1]}: {frontier}', file=sys.stderr)

  for succ in succ_map:
    succ_map_2[bbs[succ][1]] = succ_map[succ]
  # print(f'succ_map_2: {succ_map_2}', file=sys.stderr)

  # validate dom_map and dominance frontier
  for bb in bbs:
    print(f'Validating {bb[1]}', file=sys.stderr)
    paths = get_all_paths(bb[1], bbs[0][1])
    print(f'Paths to {bb[1]}: {paths}', file=sys.stderr)
    # validate dom_map
    dom_set = set(bb[1] for bb in bbs)
    for dom in dom_map[bb[1]]:
      for path in paths:
        dom_set.intersection_update(path)
        if dom not in path:
          print(f'Error: {dom} not in path {path}', file=sys.stderr)
          print(f'dom_map: {dom_map}', file=sys.stderr)
          sys.exit(1)
    dom_set.add(bb[1])
    if dom_set != dom_map[bb[1]]:
      print(f'Error: dom_set {dom_set} != dom_map[bb[1]] {dom_map[bb[1]]}', file=sys.stderr)
      sys.exit(1)
    #validate dominance frontier
    all_paths_to_everyone = [get_all_paths(b[1], bbs[0][1]) for b in bbs]
    all_paths_to_everyone_that_im_not_in = [path for paths in all_paths_to_everyone for path in paths if bb[1] not in path]
    # print(f'All paths to everyone that I am not in: {all_paths_to_everyone_that_im_not_in}', file=sys.stderr)
    for path in all_paths_to_everyone_that_im_not_in:
      for node in path:
        if bb[1] in succ_map_2:
          if node in succ_map_2[bb[1]]:
            if node not in dom_frontier(bb, cfg):
              print(f'Error: {node} not in dom frontier {dom_frontier(bb, cfg)}', file=sys.stderr)
              sys.exit(1)
            else:
              print(f'Success: {node} in dom frontier {dom_frontier(bb, cfg)}', file=sys.stderr)

# validate tree
  if not check_node(dom_map[bbs[0][1]], bbs[0][1]):
    sys.exit(1)

print(json.dumps(prog, indent=2))