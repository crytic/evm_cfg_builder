import pprint
from evm_cfg_builder.cfg import CFG

with open('token-runtime0.5.evm') as f:
    runtime_bytecode = f.read()

cfg = CFG(runtime_bytecode)

for basic_block in cfg.basic_blocks:
    print('{} -> {}'.format(basic_block, basic_block.all_outgoing_basic_blocks))
