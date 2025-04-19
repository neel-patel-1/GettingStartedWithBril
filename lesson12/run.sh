#!/bin/bash
INPUT=examples/example.bril
INPUT_JSON=examples/example.json
OUTPUT=opt/example.json
BRILI=./trace-brili/brili.ts

cat $INPUT | bril2json > $INPUT_JSON
deno run --allow-read=./examples --allow-write=. $BRILI $INPUT_JSON 10
python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON $OUTPUT
deno run --allow-read=./opt --allow-write=. $BRILI $OUTPUT 10