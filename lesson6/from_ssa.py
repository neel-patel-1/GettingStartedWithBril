import json
import sys
import queue

TERMINATORS = 'br', 'jmp', 'ret'
defs = {}
use_defs = {}
outsets = {}
pred_map = {}
succ_map = {}
dom_map = {}
dom_map_changed = True

counter = 0

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
            return True
        else:
            return False

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
        print(node.value, file=sys.stderr)
        for child in node.children:
            self.traverse(child)

    def display(self, node=None, level=0):
        if node is None:
            node = self.root
        print(' ' * level + str(node.value), file=sys.stderr)
        for child in node.children:
            self.display(child, level + 2)

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
        bbs.append((bb, bb_label,{},{},False))
        bb = []
        num_bbs += 1
        bb_label = None
    if 'label' in instr and len(bb) > 1:
      if bb_label == None:
        bb_label = get_fresh_bb_name()
      bb = bb[:-1]
      bbs.append((bb, bb_label,{},{},False))
      bb = [instr]
      bb_label = instr['label']
      num_bbs += 1
  if bb:
    if bb_label == None:
      bb_label = get_fresh_bb_name()
    bbs.append((bb, bb_label,{},{},False))
    num_bbs += 1
  return (bbs)

def initialize_bb_doms(bbs):
  global dom_map
  dom_map[bbs[0][1]] = set({bbs[0][1]})
  for bb in bbs[1:]:
    dom_map[bb[1]] = set(bb[1] for bb in bbs)


def gen_cfg(bbs):
  global pred_map
  global succ_map
  cfg = Tree(bbs[0][1])
  for index, bb in enumerate(bbs):
    if index in succ_map:
      # print(f'Adding {bb[1]} to cfg', file=sys.stderr)
      for b in succ_map[index]:
        cfg.add_node(b, bb[1])
  return cfg


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
    if tree.find_node(tree.root, node) == None:
      continue
    for child in tree.find_node(tree.root, node).children:
      if child.value not in child_set:
        child_set.add(child.value)
        q.put(child.value)

  # for each child in child_set, if bb is not in the dom_map of child, add child to dom_frontier
  for child in child_set:
    if bb[1] not in dom_map[child]:
      dom_frontier.add(child)
  return dom_frontier

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
  retry_queue = queue.Queue()
  for index, bb in enumerate(bbs):
    # for every other node except me
    for i, b in enumerate(bbs):
      if i != index:
        # if i am in the node's dom map
        if bb[1] in dom_map[b[1]]:
          print(f'{bb[1]} dominates {b[1]}', file=sys.stderr)
          # and I am not in the dom map of any of the other nodes in the dom map ( take index out of dom_map[b[1]] )
          immediately_dominates = True
          for od in dom_map[b[1]]:
            if od != bb[1] and od != b[1]:
              if bb[1] in dom_map[od]:
                immediately_dominates = False
          if immediately_dominates:
            print(f'{bb[1]} immediately dominates {b[1]}', file=sys.stderr)
            if dtree.add_node(b[1], bb[1]) == False:
              retry_queue.put((b[1], bb[1]))

  while not retry_queue.empty():
    (b, bb) = retry_queue.get()
    dtree.add_node(b, bb)
  return dtree


def bb_list_idx(bbs, bb_name):
  for index, bb in enumerate(bbs):
    if bb[1] == bb_name:
      return index
  return -1

n_ctr = 0
def gen_name():
  global n_ctr
  n_ctr += 1
  return f'v{n_ctr}'

def push_alias(name, var_renames):
  if name not in var_renames:
    var_renames[name] = [gen_name()]
  else:
    var_renames[name].append(gen_name())
  return var_renames[name][-1]

def get_alias(name, var_renames):
  if name in var_renames:
    return var_renames[name][-1]
  else:
    print(f'Error: {name} not in var_renames', file=sys.stderr)
    exit(1)

def rename_vars(bb, bbs, d_tree, var_renames):
  # rename the phi nodes destinations first since they may be consumed by subsequent instructions
  new_phi_nodes = {}
  for key, value in bb[3].items():
    new_key = push_alias(key, var_renames)
    new_phi_nodes[new_key] = [(var[0], var[1]) for var in value]
    bb[2][key] = new_key
  bb = (bb[0], bb[1], bb[2], new_phi_nodes, True) # mark that the phi node dest was renamed
  for inst in bb[0]:
    if 'dest' in inst:
      if 'args' in inst:
        for index,arg in enumerate(inst['args']):
          inst['args'][index] = get_alias(arg, var_renames)
      inst['dest'] = push_alias(inst['dest'], var_renames)
  if bb_list_idx(bbs, bb[1]) in succ_map:
    for s in succ_map[bb_list_idx(bbs, bb[1])]: #if its a successor
      for var in bbs[bb_list_idx(bbs, s)][2]: # and it has a phi node for a variable
        if var in var_renames: # and some predecessor has updated the variable
          succ_thinks_it_has_this_name = bbs[bb_list_idx(bbs, s)][2][var] # use the name the successor is expecting
          if succ_thinks_it_has_this_name not in bbs[bb_list_idx(bbs, s)][3]:
            bbs[bb_list_idx(bbs, s)][3][succ_thinks_it_has_this_name] = []
          bbs[bb_list_idx(bbs, s)][3][succ_thinks_it_has_this_name].append((get_alias(var, var_renames), bb[1])) # add this block's name for the variable to the phi node
  bbs[bb_list_idx(bbs, bb[1])] = bb
  new_bbs = bbs
  for bb in d_tree.find_node(d_tree.root, bb[1]).children:
    new_bbs = rename_vars(bbs[bb_list_idx(bbs, bb.value)], new_bbs, d_tree, var_renames)
  return new_bbs

def sub_phis_for_insts(bbs):
  for bb in bbs:
    for key, value in bb[3].items():
      phi_inst = {'op': 'phi', 'dest': key, 'args': [var[0] for var in value], 'labels': [var[1] for var in value]}
      bb[0].insert(1, phi_inst)
  return bbs


def get_repr(index,bb):
  bb_instnum = bb[1]
  return bb_instnum

def transfer(bb, inset):
  insts = bb[0]
  outset = dict(inset)
  for index, inst in enumerate(insts):
    if 'args' in inst:
      use_defs[(get_repr(index,bb))] = outset
    if 'dest' in inst:
      outset[inst['dest']] = [get_repr(index,bb)]
  return outset

def create_inset(bb,bb_list):
  global pred_map
  inset = dict()
  if bb[1] in pred_map:
    for pred in pred_map[bb[1]]:
      if bb_list[pred][1] in outsets:
        for key in outsets[bb_list[pred][1]]:
          if key in inset:
            inset[key] = inset[key] + outsets[bb_list[pred][1]][key]
          else:
            inset[key] = outsets[bb_list[pred][1]][key]
    # print(f'bb: {bb[1]} inset: {inset}')
  return inset



prog = json.load(sys.stdin)
for function in prog['functions']:
  vars = set()
  dom_map_changed = True
  dom_map.clear()
  pred_map.clear()
  succ_map.clear()

  bbs = form_bbs(function)
  form_predecessor_map(bbs)
  form_successor_map(bbs)
  succ_2_map = {}
  for i in succ_map:
    succ_2_map[bbs[i][1]] = succ_map[i]
  print(f'succ_map: {succ_2_map}', file=sys.stderr)

  for bb in bbs:
    for inst in bb[0]:
      if 'dest' in inst:
        vars.add(inst['dest'])
        if inst['dest'] not in defs:
          defs[inst['dest']] = []
        defs[inst['dest']].append(bb[1])


  if 'args' in function:
    function_args = function['args']
  else:
    function_args = None
  bbq = queue.Queue()
  for bb in bbs:
    bbq.put(bb)

  while not bbq.empty():
    bb = bbq.get()
    inset = create_inset(bb,bbs)
    if bb[1] == 'Entry' and function_args:
      for arg in function_args:
        inset[arg['name']] = 'Entry_Args'
        # print(f'bb: {bb[1]} inset: {inset}')
    if bb[1] in outsets:
      outset = outsets[bb[1]]
    else:
      outset = dict()
    new_outset = transfer(bb, inset)
    if new_outset != outset:
      outsets[bb[1]] = new_outset
      if bb[1] in succ_map:
        for succ in succ_map[bb[1]]:
          bbq.put(bbs[succ])

  # display the outsets of each bb
  for bb in bbs:
    print(f'bb: {bb[1]} outset: {outsets[bb[1]]}', file=sys.stderr)

  #Initialize the dominator map
  initialize_bb_doms(bbs)
  while dom_map_changed:
    dom_map_changed = False
    for bb in bbs[1:]:
      new_doms = get_bb_doms(bb, bbs)
      if new_doms != dom_map[bb[1]]:
        dom_map[bb[1]] = new_doms
        dom_map_changed = True
  print(f'dom_map: {dom_map}', file=sys.stderr)

  print(f'defs: {defs}', file=sys.stderr)
  # --------

  function['instrs'] = []
  new_bbs = [bb[0] for bb in bbs]
  for index,bb in enumerate(bbs):
    for inst in bb[0]:
      if 'op' in inst and inst['op'] == 'phi':
        print(inst, file=sys.stderr)
        predecessors = pred_map[bb[1]]
        # for arg in inst['args']:
          # for predecessor in predecessors:
          #   if arg in outsets[bbs[predecessor][1]]:
          #     print(f'{arg} is in {bbs[predecessor][1]}\'s outset', file=sys.stderr)
          #     new_bbs[predecessor].append({'op': 'id', 'dest': inst['dest'], 'args': [arg]})
        for label in inst['labels']:
          b_idx = bb_list_idx(bbs, label)
          new_bbs[b_idx].append({'op': 'id', 'dest': inst['dest'], 'args': [inst['args'][inst['labels'].index(label)]]})
    new_bbs[index] = [inst for inst in new_bbs[index] if 'op' not in inst or ('op' in inst and inst['op'] != 'phi')]
  for bb in new_bbs:
    function['instrs'] += bb
  print(f'function: {function}', file=sys.stderr)


print(json.dumps(prog))