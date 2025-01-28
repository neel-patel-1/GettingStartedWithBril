# Lesson 2:  Representing Programs

## Benchmark
* depends on the [bril2json utility](https://capra.cs.cornell.edu/bril/tools/brilirs.html), and [brili interpreter](https://capra.cs.cornell.edu/bril/tools/brilirs.html)
```sh
# Convert the fnv1hash bril code to json, and run it using brili
cd bench
cat fnv1_hash.bril |  bril2json  | brili
```

## Bril Program Analysis
```sh
# Run python script that counts the number of branch instructions

# Use turnt to test the analysis
```

## Basic Block && CFG Generation Algorithm
```sh
# Run python script that generates the basic blocks and CFG of a bril program and prints the result
```