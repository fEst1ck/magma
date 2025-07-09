#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout https://github.com/fEst1ck/path-cov.git "$FUZZER/path-cov"
git -C "$FUZZER/path-cov" checkout 9d8fc8c73d86e63bbec64cdb3cef5608719a88a8

git clone --no-checkout https://github.com/fEst1ck/path-cov-instr.git "$FUZZER/path-cov-instr"
git -C "$FUZZER/path-cov-instr" checkout 3928dd53557abc6fd48d76ce4882c369849c9b45

git clone --no-checkout https://github.com/fEst1ck/coverage-playground.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout 8c1e4f799d29e1cb97014b2b8a2fa6b2515ca461

git clone https://github.com/fEst1ck/fuzz-target.git "$FUZZER/fuzz-target"