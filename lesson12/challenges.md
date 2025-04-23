error: ret not allowed during speculation
* if the trace reaches a ret, we stop the trace
* how do we know where the trace stopped

speculative execution should not do anything with side effects -- traces should not contain prints

there should be a way to not execute the thing the trace replaced

speculate
<trace for code we just replaced>
commit
jmp .after_code_we_just_replaced

.recover:
<code we just replaced>

.after_code_we_just_replaced:

Nested:
speculate
<trace for code we just replaced>
commit
jmp .after_code_we_just_replaced

.recover:
<code we just replaced>

.after_code_we_just_replaced:

why?
let's say you want to conditionally execute a trace within a trace that's already conditionally executing and all the fallback code is still within that thrace -- this is the only scenario in which you would need nested speculation
can you construct a code that creates this scenario ?

nested_cond.bril:
```
@main(x: int) {
hundred: int = const 100;
cond: bool = lt x hundred;
br cond .then .else;
.then:
  cond2: bool lt x 50;
  br cond2 .then2 .else2;
  .then2:
    one: int = const 1;
    two: int = add one one;
  .else2:
    two: int = const 2;
    four: int = add two two;
.else:
  four: int = const 4;
ret;
}
```

how would you convert this into guarded traces for subsequent optimization?

* option 1 - full path through nested branches in a single trace:
main_na_1_tbd.json:
```
speculate;
hundred: int = const 100;
cond: bool = lt x hundred;
guard cond;
  cond2: bool lt x 50;
  guard cond2;
    one: int = const1;
    two: int = add one one;
```
fallback code:
```
br cond .then .else;
.then:
  cond2: bool lt x 50;
  br cond2 .then2 .else2;
  .then2:
    one: int = const 1;
    two: int = add one one;
  .else2:
    two: int = const 2;
    four: int = add two two;
.else:
  four: int = const 4;
ret;
```

* option 2 - speculate within the speculative block
```
speculate;
hundred: int = const 100;
cond: bool = lt x hundred;
guard cond;
  cond2: bool lt x 50;
  speculate;
  guard cond2;
    one: int = const1;
    two: int = add one one;
```
fallback code:
```
  // if cond2 is false, then we need to fall back to the baseline interpreter which would execute the branch instruction and
  br cond2 .then2 .else2;
  .then2:
    one: int = const 1;
    two: int = add one one;
  .else2:
    two: int = const 2;
    four: int = add two two;
```

* for inter-procedural tracing: place fallback code in a label after the last instruction we executed in the local function before taking off and executing in another function:
```
speculate:
one int = const 1;
two int = add one 1; // assume inlining pass did the variable substitution
y int = id two;
.recover:
one int = const 1;
y: int = call @foo one;
```

for option 2, guard_and_insert_trace.py must create nested speculative blocks and recovery blocks
inter-procedural or not, we can view tracing as injecting a optimized code bubble at the location where tracing started, labelling the original code which comes after, and adding a label after the orignal code that we can take assuming the trace commits successfully
* this means we need to know the last instruction of the block the trace intends to replace.
  * but what if that function falls within a callee function due to a stateful instruction like print being executed?
    * we place the stateful instruction inside the trace and cross our fingers that there are no failed guards that come after
    * we post-emptively terminate the trace before the caller's call instruction
    * we always terminate the trace before call instructions
 location original code

no hot path trace_start methodology yet, but need a way to test above trace generation methodology:
* hot path, start tracing is orthogonal and we could start with trace at all opportunities

* doing by labels introduces some other challenges: (1) we now need to find the label in the function or use null to know its before any labels, (2) we still need to go backwards - so this is same


trace code naming convention:
traces/<original_program_name>.json/<func_name>_<s_label>_<s_offset>_<e_label>_<e_offset>.json

optimized code naming convention:
traces/<original_program_name>.json/<func_name>_<s_label>_<s_offset>_<e_label>_<e_offset>.json