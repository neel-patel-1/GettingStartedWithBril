# Lesson 3:  First Optimizations

* globally unused instructions
```sh
# test globally unused instructions on simple.bril
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://deno.land/install.sh | sh

cd bril
deno install -g brili.ts

cd bril/bril-txt
uv tool install .

cd ../

cd ..//brench
uv tool install .

cd ../../first-optimizations/
brench dce.toml > results.csv
```

* lvn
```sh
# copy propagation
cat test_cases/idchain-nonlocal.bril | bril2json | tee idchain-nonlocal.json |  python3 lvn.py | python3 dce.py | bril2txt | tee idchain-nonlocal-opt.bril | bril2json | brili

# CSE
cat test_cases/redundant-dce.bril | bril2json | tee redundant-dce.json | python3 lvn.py | python3 dce.py | bril2txt | tee redundant-dce-opt.bril | bril2json | brili

# verify we handle reassignment to the same varibale name
cat test_cases/reassignment.bril | bril2json | tee reassignment.json |  python3 lvn.py | python3 dce.py | bril2txt | tee reassignment-opt.bril | bril2json | brili

# verify commutative operations can be optimized
cat test_cases/commute.bril | bril2json | tee commute.json |  python3 lvn.py | python3 dce.py | bril2txt | tee commute-opt.bril | bril2json | brili

# verify placeholders are inserted into the table when we enter a basic block with a live variable
cat test_cases/live-entry.bril | bril2json | tee live-entry.json |  python3 lvn.py | python3 dce.py | bril2txt | tee live-entry-opt.bril | bril2json | brili
```