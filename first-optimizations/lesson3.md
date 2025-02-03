# Lesson 3:  First Optimizations

* globally unused instructions
```sh
# test globally unused instructions on simple.bril
brench dce.toml > results.csv
```

* lvn
```sh
cat test_cases/idchain-nonlocal.bril | bril2json | tee idchain-nonlocal.json | python3 lvn.py |& less
```