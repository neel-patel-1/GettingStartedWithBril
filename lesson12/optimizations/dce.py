"""Trivial dead code elimination for Bril programs -- modified from sampsyo's implementation to handle traces
"""

import sys
import json

block = []

def trivial_dce_pass():
    global block
    """Remove instructions from `func` that are never used as arguments
    to any other instruction. Return a bool indicating whether we deleted
    anything.
    """
    # Find all the variables used as an argument to any instruction,
    # even once.
    used = set()
    for instr in block:
        # Mark all the variable arguments as used.
        used.update(instr.get('args', []))

    # Delete the instructions that write to unused variables.
    changed = False
    # Avoid deleting *effect instructions* that do not produce a
    # result. The `'dest' in i` predicate is true for all the *value
    # functions*, which are pure and can be eliminated if their
    # results are never used.
    new_block = [i for i in block
                    if 'dest' not in i or i['dest'] in used]

    # Record whether we deleted anything.
    changed |= len(new_block) != len(block)

    # Replace the block with the filtered one.
    block[:] = new_block

    return changed


def trivial_dce():
    """Iteratively remove dead instructions, stopping when nothing
    remains to remove.
    """
    global block
    # An exercise for the reader: prove that this loop terminates.
    while trivial_dce_pass():
        pass


def drop_killed_local(block):
    """Delete instructions in a single block whose result is unused
    before the next assignment. Return a bool indicating whether
    anything changed.
    """
    # A map from variable names to the last place they were assigned
    # since the last use. These are candidates for deletion---if a
    # variable is assigned while in this map, we'll delete what the maps
    # point to.
    last_def = {}

    # Find the indices of droppable instructions.
    to_drop = set()
    for i, instr in enumerate(block):
        # Check for uses. Anything we use is no longer a candidate for
        # deletion.
        for var in instr.get('args', []):
            if var in last_def:
                del last_def[var]

        # Check for definitions. This *has* to happen after the use
        # check, so we don't count "a = a + 1" as killing a before using
        # it.
        if 'dest' in instr:
            dest = instr['dest']
            if dest in last_def:
                # Another definition since the most recent use. Drop the
                # last definition.
                to_drop.add(last_def[dest])
            last_def[dest] = i

    # Remove the instructions marked for deletion.
    new_block = [instr for i, instr in enumerate(block)
                 if i not in to_drop]
    changed = len(new_block) != len(block)
    block[:] = new_block
    return changed


def drop_killed_pass():
    """Drop killed functions from *all* blocks. Return a bool indicating
    whether anything changed.
    """
    global block
    changed = False
    changed |= drop_killed_local(block)
    return changed


def trivial_dce_plus():
    """Like `trivial_dce`, but also deletes locally killed instructions.
    """
    global block
    while trivial_dce_pass() or drop_killed_pass():
        pass


MODES = {
    'tdce+': trivial_dce_plus,
}


def localopt():
    global block
    modify_func = trivial_dce_plus

    # Apply the change to all the functions in the input program.
    block = json.load(sys.stdin)
    modify_func()
    json.dump(block, sys.stdout, indent=2, sort_keys=True)


if __name__ == '__main__':
    localopt()
