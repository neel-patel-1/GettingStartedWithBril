### Offline Trace-Based Optimizer

* Hotness Detector: when jumping to a previous point in the program -- backedge -- we start tracing

* beginning tracing is simple -- triggered by a `jmp`
* when to stop tracing? - since the example we are working on is a doubly nested loop, maybe we stop tracing at the next backedge


* how to tell whether the jmp is a backedge from within the interpreter?
* how to create traces that enable reinsertion into the original program?
  * need start instruction
  * need last instruction
