#!/bin/bash

CLANG=clang-18
OPT=opt-18
LLVM_AS=llvm-as-18
POLYBENCH_DIR=$(pwd)/PolyBenchC-4.2.1
INCLUDES="-I${POLYBENCH_DIR}/utilities -I${POLYBENCH_DIR}/linear-algebra/kernels/atax"
FLAGS="-DPOLYBENCH_TIME"

# ├── datamining
# │   ├── correlation
# │   │   ├── correlation.c
# │   │   └── correlation.h
# │   └── covariance
# │       ├── covariance.c
# │       └── covariance.h
# ├── linear-algebra
# │   ├── blas
# │   │   ├── gemm
# │   │   │   ├── gemm.c
# │   │   │   └── gemm.h
# │   │   ├── gemver
# │   │   │   ├── gemver.c
# │   │   │   └── gemver.h
# │   │   ├── gesummv
# │   │   │   ├── gesummv.c
# │   │   │   └── gesummv.h
# │   │   ├── symm
# │   │   │   ├── symm.c
# │   │   │   └── symm.h
# │   │   ├── syr2k
# │   │   │   ├── syr2k.c
# │   │   │   └── syr2k.h
# │   │   ├── syrk
# │   │   │   ├── syrk.c
# │   │   │   └── syrk.h
# │   │   └── trmm
# │   │       ├── trmm.c
# │   │       └── trmm.h
# │   ├── kernels
# │   │   ├── 2mm
# │   │   │   ├── 2mm.c
# │   │   │   └── 2mm.h
# │   │   ├── 3mm
# │   │   │   ├── 3mm.c
# │   │   │   └── 3mm.h
# │   │   ├── atax
# │   │   │   ├── atax.c
# │   │   │   ├── atax.h
# │   │   │   ├── atax_time.ll
# │   │   │   ├── atax_time_licm
# │   │   │   ├── atax_time_licm.ll
# │   │   │   ├── atax_time_licm.o
# │   │   │   ├── atax_time_mem2reg
# │   │   │   ├── atax_time_mem2reg.ll
# │   │   │   └── atax_time_mem2reg.o
# │   │   ├── bicg
# │   │   │   ├── bicg.c
# │   │   │   └── bicg.h
# │   │   ├── doitgen
# │   │   │   ├── doitgen.c
# │   │   │   └── doitgen.h
# │   │   └── mvt
# │   │       ├── mvt.c
# │   │       └── mvt.h
# │   └── solvers
# │       ├── cholesky
# │       │   ├── cholesky.c
# │       │   └── cholesky.h
# │       ├── durbin
# │       │   ├── durbin.c
# │       │   └── durbin.h
# │       ├── gramschmidt
# │       │   ├── gramschmidt.c
# │       │   └── gramschmidt.h
# │       ├── lu
# │       │   ├── lu.c
# │       │   └── lu.h
# │       ├── ludcmp
# │       │   ├── ludcmp.c
# │       │   └── ludcmp.h
# │       └── trisolv
# │           ├── trisolv.c
# │           └── trisolv.h
# ├── medley
# │   ├── deriche
# │   │   ├── deriche.c
# │   │   └── deriche.h
# │   ├── floyd-warshall
# │   │   ├── floyd-warshall.c
# │   │   └── floyd-warshall.h
# │   └── nussinov
# │       ├── Nussinov.orig.c
# │       ├── nussinov.c
# │       └── nussinov.h
# ├── polybench.pdf
# ├── stencils
# │   ├── adi
# │   │   ├── adi.c
# │   │   └── adi.h
# │   ├── fdtd-2d
# │   │   ├── fdtd-2d.c
# │   │   └── fdtd-2d.h
# │   ├── heat-3d
# │   │   ├── heat-3d.c
# │   │   └── heat-3d.h
# │   ├── jacobi-1d
# │   │   ├── jacobi-1d.c
# │   │   └── jacobi-1d.h
# │   ├── jacobi-2d
# │   │   ├── jacobi-2d.c
# │   │   └── jacobi-2d.h
# │   └── seidel-2d
# │       ├── seidel-2d.c
# │       └── seidel-2d.h

PASS=$(pwd)/../build/licm/LICMPass.so

# gcc -O3 -I ${POLYBENCH_DIR}/utilities -I ${POLYBENCH_DIR}/linear-algebra/kernels/atax ${POLYBENCH_DIR}/utilities/polybench.c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time

${CLANG} ${FLAGS} -c ${POLYBENCH_DIR}/utilities/polybench.c -o ${POLYBENCH_DIR}/utilities/polybench.o


${CLANG} ${FLAGS} -S -O1 -Xclang -disable-llvm-passes -emit-llvm ${INCLUDES} -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax.c -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time.ll

# normal time
${OPT} -passes=mem2reg -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time.ll -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.o -c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.o ${POLYBENCH_DIR}/utilities/polybench.o

# licm time
${OPT} -load-pass-plugin ${PASS} -passes=licm-invariant -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.o -c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.o ${POLYBENCH_DIR}/utilities/polybench.o

BENCHMARKS=( "datamining/correlation" "datamining/covariance" "linear-algebra/blas/gemm" "linear-algebra/blas/gemver" "linear-algebra/blas/gesummv" "linear-algebra/blas/symm" "linear-algebra/blas/syr2k" "linear-algebra/blas/syrk" "linear-algebra/blas/trmm" "linear-algebra/kernels/2mm" "linear-algebra/kernels/3mm" "linear-algebra/kernels/atax" "linear-algebra/kernels/bicg" "linear-algebra/kernels/doitgen" "linear-algebra/kernels/mvt" "linear-algebra/solvers/cholesky" "linear-algebra/solvers/durbin" "linear-algebra/solvers/gramschmidt" "linear-algebra/solvers/lu" "linear-algebra/solvers/ludcmp" "linear-algebra/solvers/trisolv" "medley/deriche" "medley/floyd-warshall" "medley/nussinov" "stencils/adi" "stencils/fdtd-2d" "stencils/heat-3d" "stencils/jacobi-1d" "stencils/jacobi-2d" "stencils/seidel-2d")
for benchmark in "${BENCHMARKS[@]}"; do
    echo "Compiling ${benchmark}..."
    DIR="${POLYBENCH_DIR}/${benchmark}"
    FILE="${DIR}/$(basename ${DIR}).c"
    if [ -f "${FILE}" ]; then
        ${CLANG} ${FLAGS} -S -O1 -Xclang -disable-llvm-passes -emit-llvm ${INCLUDES} -S ${FILE} -o ${DIR}/$(basename ${DIR}).ll

        # normal time
        ${OPT} -passes=mem2reg -S ${DIR}/$(basename ${DIR}).ll -o ${DIR}/$(basename ${DIR})_mem2reg.ll
        ${CLANG} -o ${DIR}/$(basename ${DIR})_mem2reg.o -c ${DIR}/$(basename ${DIR})_mem2reg.ll
        ${CLANG} -o ${DIR}/$(basename ${DIR})_mem2reg ${DIR}/$(basename ${DIR})_mem2reg.o ${POLYBENCH_DIR}/utilities/polybench.o -lm

        # licm time
        ${OPT} -load-pass-plugin ${PASS} -passes=licm-invariant -S ${DIR}/$(basename ${DIR})_mem2reg.ll -o ${DIR}/$(basename ${DIR})_licm.ll
        ${CLANG} -o ${DIR}/$(basename ${DIR})_licm.o -c ${DIR}/$(basename ${DIR})_licm.ll
        ${CLANG} -o ${DIR}/$(basename ${DIR})_licm ${DIR}/$(basename ${DIR})_licm.o ${POLYBENCH_DIR}/utilities/polybench.o -lm

    else
        echo "File not found: ${FILE}"
    fi
done