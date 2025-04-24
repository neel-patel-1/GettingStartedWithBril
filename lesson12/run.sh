#!/bin/bash
FNAME=$1
ARGS="${@:2}"
if [ -z "$FNAME {ARGS}" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi
INPUT=examples/${FNAME}.bril
INPUT_JSON=examples/${FNAME}.json
TRACE_DIR=./traces/${FNAME}.json
OPT_TRACES=./opt/traces/${FNAME}.json/
OUTPUT=opt/${FNAME}.json
TRACE_BRILI=./trace-brili/brili.ts
OG_BRILI=brili

rm -rf $TRACE_DIR $OPT_TRACES $OUTPUT $INPUT_JSON guarded/traces/$FNAME.json
cat $INPUT | bril2json > $INPUT_JSON
# run through trace brili to generate the traces
deno run --allow-read=./examples --allow-write=. $TRACE_BRILI $INPUT_JSON -p ${ARGS}
brili -p ${ARGS} < $INPUT_JSON
echo "Before optimization: "
echo "-----------------------"
bril2txt < $INPUT_JSON

  # apply optimizations to the trace
mkdir -p $OPT_TRACES
for trace in ${TRACE_DIR}/*; do
  python3 ./optimizations/inline.py ${INPUT_JSON} ${trace} | python3 optimizations/lvn.py  -p -f | python3 optimizations/dce.py > $OPT_TRACES/$(basename $trace)
  #python3 ./optimizations/inline.py ${INPUT_JSON} ${trace} | python3 optimizations/lvn.py  -p -f > $OPT_TRACES/$(basename $trace)
done

# re-insert the traces
echo "After optimization: "
echo "-----------------------"
python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON > $OUTPUT
bril2txt < $OUTPUT
brili -p ${ARGS} < $OUTPUT