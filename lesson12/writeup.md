### Offline Trace-Based Optimizer
This task was a collaboration between @arnavm30 and @neel-patel-1. We implemented an ahead-of-time, interprocedural, trace-based optimizer which uses intruction counts for hotness detection.

* **Hotness detection && Trace Collection**: We modify the baseline `brili` interpreter to implement hot code detection and trace collection. For hot code detection, we add a counter to the `Op`object to count the number of times an instruction is executed. When a *hotness_threshold* (2 in our implementation) is reached, `trace-brili` will begin emitting instructions to a trace file.
* **Trace Optimization and Insertion**: Traces are optimized in a multi-stage pipeline. First traces are passed through `inline.py` to remove call and ret instructions, substitute arguments with the caller's variable names and handle any naming conflicts within the callee. Next, they are passed through `lvn.py` for local value numbering and `tdce.py` for dead code elimination. To prepare traces for insertion back into the original program,  `optimize_and_insert_trace.py` (1) wraps the optimized trace with a pair of *speculate* and *commit* instructions, (2) replaces each branch with a guard instruction, and (3) uses `trace-brili`'s <func>_<start_label>_<start_label_offset>_<end_label>_<end_label_offset> trace naming convention to find the code location to insert the optimized trace.

One interesting aspect of our implementation that highlights a challenge with trace insertion in an ahead-of-time, trace-based optimizer is shown in the below example when the optimizer is applied to code containing a loop. Before optimization [hot_loop.bril's]() loop body executes five times:
```
@main(x: int) {
  one: int = const 1;
  five: int = const 5;

  it: int = id one;
  accum: int = const 0;

.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;

.for.body:
  it: int = add it one;
  accum: int = add accum it;

  jmp .for.header;

.for.done:
  print accum;
  ret;
}
```
on the second iteration, the loop header and body become hot, so `trace-brili` begins collecting instructions. The trace contains only the hot instructions from the executed instruction sequence, so is missing the first iteration of the loop:
```
.for.header:
.for.body:
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
```

Such a trace would cause the program to produce incorrect results. To address this, we pass traces through `fill_labels.py` before subsequent optimizations. `fill_labels.py` can detect whether a trace contains a loop and fill in any missing iterations:
```
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
.for.body:
  it: int = add it one;
  accum: int = add accum it;
  jmp .for.header;
.for.header:
  cond: bool = lt it five;
  br cond .for.body .for.done;
```

We run our optimizer on three of our own examples and one core bril benchmark.
* `hot_loop` tests our optimizers ability to detect hot loop headers/bodies and generate correct, optimized traces
* `dead_code_inline` redefines a set of local variables in a callee function. Since our optimizer constructs inter-procedural traces, it inlines functions and eliminates the redundant variables.
* `assign_and_print` repeatedly assigns to a variable and prints immediately. Since traces are emitted when operations with side-effects (prints) are invoked, this example generates many small traces.
* TODO: benchmark

| Program           | Dyn Inst Count (Unoptimized)  | Dyn Inst Count (w/ Trace-based Opts ) |
|-------------------|-------------------------------|-----------------------------|
| `hot_loop`        | 30                            | 26                          |
| `dead_code_inline`| 134                           | 141                        |
| `assign_and_print`| 60                            | 150                         |
| `BENCHMARK`       | TBD                           | TBD                         |