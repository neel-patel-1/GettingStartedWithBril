#!/bin/bash
BRILI=./trace-brili/brili.ts
cat examples/example.bril | bril2json | deno run --allow-write=. $BRILI 10
