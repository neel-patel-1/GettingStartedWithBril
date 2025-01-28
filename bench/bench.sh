#!/bin/bash

cat fnv1_hash.bril |  bril2json | tee fnv1_hash.json  | brili
