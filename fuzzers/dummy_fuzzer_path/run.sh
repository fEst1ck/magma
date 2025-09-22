#!/bin/bash

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env SHARED: path to directory shared with host (to store results)
# - env PROGRAM: name of program to run (should be found in $OUT)
# - env ARGS: extra arguments to pass to the program
# - env FUZZARGS: extra arguments to pass to the fuzzer
##

mkdir -p "$SHARED/findings"

export CFG_FILE="$FUZZER/coverage/coverage.json"

"$FUZZER/dummy-fuzzer" -i "$TARGET/corpus/$PROGRAM" -o "$SHARED/findings" \
	-j 0 -c block,edge,pfp,quad,path,rawpath -u edge,path \
    $FUZZARGS -- "$OUT/$PROGRAM" $ARGS 2>&1