#!/bin/bash
BRILI=./trace-brili/brili.ts
cat example.bril | bril2json | deno run --allow-write=. $BRILI 10
