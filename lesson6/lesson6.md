### Lesson 6: Convert to/from ssa


works with args:
bril2json < bril2json < test_cases/arg_reassign.bril | brili 1 5 | brili 1 5
bril2json < test_cases/arg_reassign.bril | python3 ssa.py | bril2txt | tee arg_reassign.ssa
bril2json < arg_reassign.ssa | python3 from_ssa.py  | brili 1 5

* validate the to ssa conversion
```sh
turnt --save ./benchmarks/*.bril
```

```sh
for i in  ./benchmarks/*.bril; do bril2json < $i | python3 ssa.py | bril2txt | tee $i.ssa ; done
mv ./benchmarks/*.ssa ./phi_benchs/
for i in phi_benchs/*; do bril2json < ${i} | python3 ./from_ssa.py | bril2txt | tee ${i}.back; done
```

for some reason we end up using an undefined variable after converting back from ssa, where in the original program we do not

it looks like

.check_result:
...
br cond .b1 .b2

.process_result:
...
v12 =
...

.check_done:
...
v20 = id v12
...

if .process_result is not executed, then v12 is undefined, but we still use it in .check_done

originally it was:
 .check_result:
    print result;
    processed: bool = call @is_single_digit result;
    br processed .check_done .process_result;
 .process_result:
    r0: int = call @peel_last_digit result;
    result: int = div result ten;
    result: int = add result r0;
    jmp .check_result;

 .check_done:
    done: bool = eq input zero;
    br done .done .begin;

would passing through dead code elimination fix this?

bril2json <  digital-root.back | python3 ../first-optimizations/lvn.py | python3 ../first-optimizations/dce.py | bril2txt | tee digital-root.back.lvn.dce

