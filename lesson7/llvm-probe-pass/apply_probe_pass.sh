#!/bin/bash
# clang -emit-llvm -S -o - something.c
mkdir -p build
cd build
cmake ..
make
cd ..
clang -fpass-plugin=build/probe/ProbePass.so  something.c