#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout https://github.com/fEst1ck/path-cov.git "$FUZZER/path-cov"
git -C "$FUZZER/path-cov" checkout 9d8fc8c73d86e63bbec64cdb3cef5608719a88a8

git clone --no-checkout https://github.com/fEst1ck/path-cov-instr.git "$FUZZER/path-cov-instr"
git -C "$FUZZER/path-cov-instr" checkout 2e94edf3b7b9f811b6eae08f4b4b94a36ee0a48c

git clone --no-checkout https://github.com/fEst1ck/coverage-playground.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout a857280e36a9a1a4f05e40623fd8c3f2f9e08094

git clone https://github.com/fEst1ck/fuzz-target.git "$FUZZER/fuzz-target"

wget -O "$FUZZER/StandaloneFuzzTargetMain.c" https://raw.githubusercontent.com/llvm/llvm-project/main/compiler-rt/lib/fuzzer/standalone/StandaloneFuzzTargetMain.c
mv "$FUZZER/StandaloneFuzzTargetMain.c" "$FUZZER/fuzz-target/FuzzTarget.c"