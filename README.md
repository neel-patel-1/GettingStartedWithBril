# Lesson 2:  Representing Programs

## Benchmark
* depends on the [bril2json utility](https://capra.cs.cornell.edu/bril/tools/brilirs.html), and [brili interpreter](https://capra.cs.cornell.edu/bril/tools/brilirs.html)
* and [turnt](https://github.com/cucapra/turnt) for creating test outputs
```sh
# Convert the fnv1hash bril code to json, and run it using brili
cd bench
cat fnv1_hash.bril |  bril2json  | brili

# Use turnt to create the expected benchmark output (the hash) in fnv1_hash.out
turnt --save fnv1_hash.bril
```

## Bril Basic Block Generation, CFG Generation, and Program Analysis
```sh
# Run python script that generates the basic blocks and CFG of a bril program and counts the number of add instructions
python3 tools/bb.py
```
