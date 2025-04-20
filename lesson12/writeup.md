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


```
  lvn.2: int = const 1;
  hundred: int = const 100;
  cond: bool = lt x hundred;
  br cond .then .else;
.then:
  y: int = call @f x;  // wait for ret to do an assignment
  one: int = const 1;
  b: int = sub a one; // replace a with x
  ret b; // assign y to b
  jmp .done;
.done:
  print y;
  ret;

      "name": "f",
      "type": "int"
      "args": [
        {
          "name": "a",
          "type": "int"
        }
      ],

.then:
  one: int = const 1;
  b: int = sub x one; // replace a with x
  y: int = id b;
  jmp .done;
.done:
  print y;
  ret;

  lvn.2: int = const 1;
  hundred: int = const 100;
  cond: bool = lt x hundred;
  br cond .then .else;
.then:
  y: int = call @f x;  // wait for ret to do an assignment
  one: int = const 1;
  v1: int = sub x one; // replace a with x
  ret v1; // assign y to b
  y: int = id v1;
  jmp .done;
.done:
  print x;
  ret;
```


  y: int = call @f x;  // wait for ret to do an assignment

  for all the instructions up until the next "ret", replace any instance of functions[name][args][any_index] with inst[args][the_corresponding_index]