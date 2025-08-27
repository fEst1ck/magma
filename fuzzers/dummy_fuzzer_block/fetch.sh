#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout https://github.com/fEst1ck/path-cov.git "$FUZZER/path-cov"
git -C "$FUZZER/path-cov" checkout 9d8fc8c73d86e63bbec64cdb3cef5608719a88a8

git clone --no-checkout https://github.com/fEst1ck/path-cov-instr.git "$FUZZER/path-cov-instr"
git -C "$FUZZER/path-cov-instr" checkout c9332589b19c1d714cf647819771f0de4ca91d07

git clone --no-checkout https://github.com/fEst1ck/coverage-playground.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout 5bd586397f82abfc00b4b86458aa70ddd0f8add6

git clone https://github.com/fEst1ck/fuzz-target.git "$FUZZER/fuzz-target"

wget -O "$FUZZER/StandaloneFuzzTargetMain.c" https://raw.githubusercontent.com/llvm/llvm-project/main/compiler-rt/lib/fuzzer/standalone/StandaloneFuzzTargetMain.c
mv "$FUZZER/StandaloneFuzzTargetMain.c" "$FUZZER/fuzz-target/FuzzTarget.c"