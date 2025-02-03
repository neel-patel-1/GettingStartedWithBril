# Lesson 3:  First Optimizations

* globally unused instructions
```sh
# test globally unused instructions on simple.bril
brench dce.toml > results.csv
```

* lvn
```sh
cat test_cases/idchain-nonlocal.bril | bril2json | tee idchain-nonlocal.json |  python3 lvn.py | python dce.py | bril2txt | tee idchain-opt.bril | bril2json | brili
cat test_cases/redundant-dce.bril | bril2json | tee redundant-dce.json | python3 lvn.py | python dce.py | bril2txt | tee redundant-dce-opt.bril | bril2json | brili
```