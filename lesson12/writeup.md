### Offline Trace-Based Optimizer

* Trace Collection: aggregate traces in a list of bril.Instructions and output them to a file as soon as a "trace abort" condition is met
  * traces are kept in traces/<func>_<start_inst_no>.json

* Trace Insertion:
  * traces contain dynamically executed instructions
  * `lvn.py` takes an input program and uses traces produced by `trace-brili` to produce an output program with optimized traces containing guard instructions that, if activated cause a jump to a *.recover* label
    * currently:
      * tracing begins at the beginning of main
      * all guard statements are placed at the top of the trace, so no state is rolled back -- the recovery block is just the original program

* Hotness Detector: None - currently start tracing at main function

* Implementation Details:
  * in the case of multiple traces collected for the same function, performing an insertion would invalidate the offsets for other trace files if performed sequentially -- we start with the last trace (highest <start_inst_no>.json out of all <func>_<start_inst_no>.json traces with the same <func>)