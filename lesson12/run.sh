#!/bin/bash
INPUT=examples/example.bril
INPUT_JSON=examples/example.json
TRACE_DIR=./traces/example.json
OPT_TRACES=./opt/traces/example.json/
OUTPUT=opt/example.json
TRACE_BRILI=./trace-brili/brili.ts
OG_BRILI=brili

cat $INPUT | bril2json > $INPUT_JSON
# run through trace brili to generate the traces
deno run --allow-read=./examples --allow-write=. $TRACE_BRILI $INPUT_JSON -p 10
echo "Before optimization: "
echo "-----------------------"
bril2txt < $INPUT_JSON

  # apply optimizations to the trace
for trace in ${TRACE_DIR}/*; do
  python3 ./optimizations/inline.py ${INPUT_JSON} ${trace} | python3 optimizations/lvn.py  -p -f | python3 optimizations/dce.py > $OPT_TRACES/$(basename $trace)
done

# re-insert the traces
echo "After optimization: "
echo "-----------------------"
python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON > $OUTPUT
bril2txt < $OUTPUT
brili -p 10 < $OUTPUT