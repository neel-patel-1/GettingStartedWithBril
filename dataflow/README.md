## Dataflow Analysis

### Benchmark Performance
* Run all benchmarks
```sh
brench ./dataflow.toml > results.csv
python3 plot.py < results.csv
```


### Test Cases
* Print use-def chains
```sh
bril2json < ../bril/examples/test/df/fact.bril | python3 ./reaching_defs.py
```

* Live variables only
```sh
bril2json < ./test_cases/dead_d.bril | python3 ./live_variables.py  | bril2txt
```