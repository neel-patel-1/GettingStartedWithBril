### Offline Trace-Based Optimizer

* Hotness Detector: when jumping to a previous point in the program -- backedge -- we start tracing

* beginning tracing is simple -- triggered by a `jmp`
* when to stop tracing? - since the example we are working on is a doubly nested loop, maybe we stop tracing at the next backedge


* how to tell whether the jmp is a backedge from within the interpreter?
* how to create traces that enable reinsertion into the original program?
  * need start instruction
  * need last instruction

[speculate](https://capra.cs.cornell.edu/bril/lang/spec.html) enables rollback when the guard is triggered
* the code is morphed to be speculative with the guards we want to enforce
* what condition do we want to enforce -- a literal condition -- e.g., a branch is not triggered that continues the loop and multiplies v by 2 instead of proceeding to the inner 15 increment loop