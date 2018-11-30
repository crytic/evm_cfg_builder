import pprint
from evm_cfg_builder.cfg import CFG

with open('token-runtime.evm') as f:
    runtime_bytecode = f.read()

cfg = CFG(runtime_bytecode)

pprint.pprint(cfg.export_basic_blocks())

# You can also export the functions information (which includes the basic blocks)
#pprint.pprint(cfg.export_functions())
