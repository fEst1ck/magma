#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout https://github.com/fEst1ck/path-cov.git "$FUZZER/path-cov"
git -C "$FUZZER/path-cov" checkout 1812e656e1d1ff8b4f2c944d025680c4c279737b

git clone --no-checkout https://github.com/fEst1ck/path-cov-instr.git "$FUZZER/path-cov-instr"
git -C "$FUZZER/path-cov-instr" checkout d1d446acda5aaec78e58a2a8e077745cface19b2

git clone --no-checkout https://github.com/fEst1ck/coverage-playground.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout 7174216f0be724698602b726cd81888b9b76c29d

git clone https://github.com/fEst1ck/fuzz-target.git "$FUZZER/fuzz-target"

wget -O "$FUZZER/StandaloneFuzzTargetMain.c" https://raw.githubusercontent.com/llvm/llvm-project/main/compiler-rt/lib/fuzzer/standalone/StandaloneFuzzTargetMain.c
mv "$FUZZER/StandaloneFuzzTargetMain.c" "$FUZZER/fuzz-target/FuzzTarget.c"