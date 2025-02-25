### Lesson 6: Convert to/from ssa

* validate the to ssa conversion
```sh
turnt --save ./benchmarks/*.bril
```

```sh
for i in  ./benchmarks/*.bril; do bril2json < $i | python3 ssa.py | bril2txt | tee $i.ssa ; done
mv ./benchmarks/*.ssa ./phi_benchs/
for i in phi_benchs/*; do bril2json < ${i} | python3 ./from_ssa.py | bril2txt | tee ${i}.back; done
```