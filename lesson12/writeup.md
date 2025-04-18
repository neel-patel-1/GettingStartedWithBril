### Offline Trace-Based Optimizer

* Hotness Detector: None - currently start tracing at main function

* Trace Collection: aggregate traces in a list of bril.Instructions and output them to a file as soon as a "trace abort" condition is met
  * traces are kept in traces/<func>_<start_inst_no>.json

* Trace Optimization: apply LVN to the instruction trace, aggregating conditional instructions as they occur, turning them into guard instructions, which are hoisted to the top of the trace

* Trace Insertion:
  * traces contain dynamically executed instructions
  * so we need to know the insertion point, all the conditions that must be met (in guard instructions at the top of the optimized trace), and the failback code (placed at the bottom of the optimized trace)
    * if all the guard conditions are met, the optimized code is safe to run, a .recover label is placed after the optimized code -- effectively acting as an else condition (where the optimized code would be in the if block)
  * in the case of multiple traces collected for the same function, performing an insertion would invalidate the offsets for other trace files if performed sequentially -- we start with the last trace (highest <start_inst_no>.json out of all <func>_<start_inst_no>.json traces with the same <func>)