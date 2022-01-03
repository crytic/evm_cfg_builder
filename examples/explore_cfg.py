import sys
from evm_cfg_builder.cfg.cfg import CFG

if len(sys.argv) != 2:
    print('Usage python explore_cfg.py contract.evm')
    sys.exit(-1)

with open(sys.argv[1], encoding="utf-8") as f:
    runtime_bytecode = f.read()

cfg = CFG(runtime_bytecode)

for basic_block in cfg.basic_blocks:
    print(f'{basic_block} -> {sorted(basic_block.all_outgoing_basic_blocks, key=lambda x:x.start.pc)}')
