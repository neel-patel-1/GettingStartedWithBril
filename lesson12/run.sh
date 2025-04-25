#!/bin/bash
FNAME=$1
H_THRESH=2
for arg in "$@"; do
  if [[ $arg == "-h="* ]]; then
    H_THRESH=${arg#-h=}
    break
  fi
done
ARGS=$(for arg in "${@:2}"; do [[ $arg != -h=* ]] && echo -n "$arg "; done)
if [ -z "$FNAME {ARGS}" ]; then
  echo "Usage: $0 <filename> [-h=<threshold>] [additional arguments]"
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
deno run --allow-read=./examples --allow-write=. $TRACE_BRILI $INPUT_JSON -h ${H_THRESH} -p ${ARGS}
brili -p ${ARGS} < $INPUT_JSON
echo "Before optimization: "
echo "-----------------------"
bril2txt < $INPUT_JSON

mkdir -p $OPT_TRACES
rm -rf filled/
mkdir -p filled/$(basename $INPUT_JSON)
no=0
for trace in ${TRACE_DIR}/*; do
  cp $trace $OPT_TRACES/$(basename $trace)
  cp $trace ./trace_og_nofill
  python3 optimizations/fill_labels.py $trace > filled/filled_${no}
  cp -f filled/filled_${no} $trace
  cp -f filled/filled_${no} $OPT_TRACES/$(basename $trace)
  no=$((no + 1))
done
echo "Reinserted Traces -- No Optimizations: "
python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON > $OUTPUT
bril2txt < $OUTPUT
brili -p ${ARGS} < $OUTPUT

  # apply optimizations to the trace
for trace in ${TRACE_DIR}/*; do
  python3 ./optimizations/inline.py ${INPUT_JSON} ${trace} | python3 optimizations/lvn.py  -p -f > $OPT_TRACES/$(basename $trace)
done

# re-insert the traces
echo "After optimization: "
echo "-----------------------"
python3 ./optimizations/optimize_and_insert_trace.py $INPUT_JSON | python3 ../bril/examples/tdce.py tdce+ > $OUTPUT
bril2txt < $OUTPUT
brili -p ${ARGS} < $OUTPUT