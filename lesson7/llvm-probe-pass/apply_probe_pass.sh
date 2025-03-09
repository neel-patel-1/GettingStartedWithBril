#!/bin/bash
# clang -emit-llvm -S -o - something.c
clang -fpass-plugin=llvm-pass-skeleton/build/skeleton/SkeletonPass.so  something.c