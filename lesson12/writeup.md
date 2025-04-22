### Offline Trace-Based Optimizer

* Trace Collection: `trace-brili` emits traces of dynamically executed instructions
* Trace Optimization and Insertion: traces are passed through `inline.py` to remove call and ret instructions, substitute the caller's variable names and rename conflicting variable names in the callee, then `lvn.py` and `dce.py` for optimization, and finally, `guard_and_insert_trace.py` which transforms branches into guards and creates a .recover label to return to normal execution if any guard fails
