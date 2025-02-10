## Dataflow Analysis

* Print use-def chains
```sh
bril2json < ../bril/examples/test/df/fact.bril | python3 ./reaching_defs.py
```

* Live variables only
```sh
bril2json < ./test_cases/dead_d.bril | python3 ./live_variables.py  | bril2txt
```