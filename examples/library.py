import pprint
from evm_cfg_builder.cfg import CFG

with open('token-runtime.evm') as f:
    runtime_bytecode = f.read()

cfg = CFG(runtime_bytecode)

for function in cfg.functions:
    print('Function {}'.format(function.name))
    # Each function may have a list of attributes
    # An attribute can be:
    # - payable
    # - view
    # - pure
    if function.attributes:
        print('\tAttributes:')
        for attr in function.attributes:
            print('\t\t-{}'.format(attr))

    print('\n\tBasic Blocks:')
    for basic_block in function.basic_blocks:
        # Each basic block has a start and end instruction
        # instructions are pyevmasm.Instruction objects
        print('\t- 0x{} - 0x{}'.format(basic_block.start.pc,
                                       basic_block.end.pc))

        for ins in basic_block.instructions:
            print('\t  {}'.format(ins.name))

        print()

