#!/bin/bash

CLANG=clang-18
OPT=opt-18
LLVM_AS=llvm-as-18
POLYBENCH_DIR=$(pwd)/PolyBenchC-4.2.1
INCLUDES="-I${POLYBENCH_DIR}/utilities -I${POLYBENCH_DIR}/linear-algebra/kernels/atax"
FLAGS="-DPOLYBENCH_TIME"

PASS=$(pwd)/../build/licm/LICMPass.so


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