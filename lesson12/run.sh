#!/bin/bash
INPUT=examples/example.bril
INPUT_JSON=examples/example.json
BRILI=./trace-brili/brili.ts

cat $INPUT | bril2json > $INPUT_JSON
deno run --allow-read=./examples --allow-write=. $BRILI $INPUT_JSON 10