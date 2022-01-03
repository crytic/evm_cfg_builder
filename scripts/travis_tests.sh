#!/usr/bin/env bash

python examples/explore_cfg.py examples/token-runtime.evm | sort > tmp_explore_cfg.txt

DIFF=$(diff tmp_explore_cfg.txt examples/expected_output/explore_cfg.txt)
if [  "$DIFF" != "" ] 
then
    echo "explore_cfg failed"
    echo $DIFF
    exit 255
fi

python examples/explore_functions.py examples/token-runtime.evm > tmp_explore_functions.txt

DIFF=$(diff tmp_explore_functions.txt examples/expected_output/explore_functions.txt)
if [  "$DIFF" != "" ] 
then
    echo "explore_functions failed"
    echo $DIFF
    #exit -1
fi

evm-cfg-builder tests/fomo3d.evm --export-dot fomo3d-output
for f in $(find tests/expected-fomo3d-output/*)
do
    # Compare the sorted version of the dot files
    # It's not perfect, but it avoids dealing with similar dot files
    # generated in a different order
    DIFF=$(diff <(sort $f) <(sort fomo3d-output/${f##*/}))
    if [  "$DIFF" != "" ] 
    then
        echo "fomo3d dot failed"
        echo $f
        echo $DIFF
        exit 255
    fi
done
