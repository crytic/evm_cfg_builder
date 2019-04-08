

python examples/explore_cfg.py examples/token-runtime.evm | sort > tmp_explore_cfg.txt

DIFF=$(diff tmp_explore_cfg.txt examples/expected_output/explore_cfg.txt)
if [  "$DIFF" != "" ] 
then
    echo "explore_cfg failed"
    cat tmp_explore_cfg.txt 
    echo ""
    cat examples/expected_output/explore_cfg.txt
    exit -1
fi

python examples/explore_functions.py examples/token-runtime.evm > tmp_explore_functions.txt

DIFF=$(diff tmp_explore_functions.txt examples/expected_output/explore_functions.txt)
if [  "$DIFF" != "" ] 
then
    echo "explore_functions failed"
    cat tmp_explore_functions.txt 
    echo ""
    cat examples/expected_output/explore_functions.txt
    exit -1
fi
