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