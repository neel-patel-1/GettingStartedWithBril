#!/bin/bash
INPUT=examples/example.bril
INPUT_JSON=examples/example.json
TRACE_DIR=./traces/example.json
OPT_TRACES=./opt/traces/example.json/
OUTPUT=opt/example.json
TRACE_BRILI=./trace-brili/brili.ts
OG_BRILI=brili

cat $INPUT | bril2json > $INPUT_JSON
deno run --allow-read=./examples --allow-write=. $TRACE_BRILI $INPUT_JSON -p 10
for trace in ${TRACE_DIR}/*; do
  echo "Before optimization: "
  echo "-----------------------"
  bril2txt < $INPUT_JSON
  python3 ./optimizations/inline.py ${INPUT_JSON} ${trace} | python3 optimizations/lvn.py  -p -f | python3 optimizations/dce.py > $OPT_TRACES/$(basename $trace)
  echo "After optimization: "
  echo "-----------------------"
  python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON $OUTPUT | bril2txt
done