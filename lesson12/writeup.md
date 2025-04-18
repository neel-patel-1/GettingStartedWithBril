### Offline Trace-Based Optimizer

* Hotness Detector: None - currently start tracing at main function

* Trace Collection: aggregate traces in a list of bril.Instructions and output them to a file as soon as a "trace abort" condition is met

* Trace Optimization: apply LVN to the instruction trace, aggregating conditional instructions as they occur, turning them into guard instructions, which are hoisted to the top of the trace