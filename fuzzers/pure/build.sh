#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

export PATH="/root/.cargo/bin:${PATH}"

# cd "$FUZZER/path-cov-instr"
# make
# cp libCodeCoveragePass.so $FUZZER/libCodeCoveragePass.so
# cp coverage_runtime.o $FUZZER/coverage_runtime.o
# cp path-clang $FUZZER/path-clang
# cp path-clang++ $FUZZER/path-clang++
# cd -

# cd "$FUZZER/repo"
# rm Cargo.lock
# cargo build --release
# cp target/release/dummy-fuzzer $FUZZER/dummy-fuzzer
# cd -

cd "$FUZZER/fuzz-target"
clang -O2 -c FuzzTarget.c
ar rc $FUZZER/libStandaloneFuzzTarget.a FuzzTarget.o
cd -