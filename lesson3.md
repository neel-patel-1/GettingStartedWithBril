# Lesson 3:  First Optimizations

* globally unused instructions
```sh
cat tools/benchmarks/ackermann.bril | bril2json | tee ackermann.json | python3 first-optimizations/globally_unused_insts.py
```
