# Lesson 3:  First Optimizations

* globally unused instructions
```sh
# test globally unused instructions on simple.bril
brench dce.toml > results.csv
```

* lvn
```sh
# copy propagation
cat test_cases/idchain-nonlocal.bril | bril2json | tee idchain-nonlocal.json |  python3 lvn.py | python dce.py | bril2txt | tee idchain-opt.bril | bril2json | brili

# CSE
cat test_cases/redundant-dce.bril | bril2json | tee redundant-dce.json | python3 lvn.py | python dce.py | bril2txt | tee redundant-dce-opt.bril | bril2json | brili

# handling reassignment to the same varibale name
cat test_cases/reassignment.bril | bril2json | tee reassignment.json |  python3 lvn.py | python dce.py | bril2txt | tee reassignment.bril | bril2json | brili
```