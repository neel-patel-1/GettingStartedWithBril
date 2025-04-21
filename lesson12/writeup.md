### Offline Trace-Based Optimizer

* Trace Collection: `trace-brili` emits traces of dynamically executed instructions
* Trace Optimization and Insertion: traces are passed through `inline.py` to remove superfluous call and ret instructions and handle conflicting variable names, then `lvn.py` and `dce.py`, and finally, `guard_and_insert_trace.py` which transforms conditional jumps into guard instructions and creates a .recover label to return to normal execution if any guard fails
