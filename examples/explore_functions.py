import sys
from evm_cfg_builder.cfg.cfg import CFG

if len(sys.argv) != 2:
    print('Usage python explore_functions.py contract.evm')
    sys.exit(-1)

with open(sys.argv[1], encoding="utf-8") as f:
    runtime_bytecode = f.read()

cfg = CFG(runtime_bytecode)

for function in sorted(cfg.functions, key=lambda x: x.start_addr):
    print(f'Function {function.name}')
    # Each function may have a list of attributes
    # An attribute can be:
    # - payable
    # - view
    # - pure
    if sorted(function.attributes):
        print('\tAttributes:')
        for attr in function.attributes:
            print(f'\t\t-{attr}')

    print('\n\tBasic Blocks:')
    for basic_block in sorted(function.basic_blocks, key=lambda x:x.start.pc):
        # Each basic block has a start and end instruction
        # instructions are pyevmasm.Instruction objects
        print(f'\t- @{len(basic_block.start.pc)}-{hex(basic_block.end.pc)}')

        print('\t\tInstructions:')
        for ins in basic_block.instructions:
            print(f'\t\t- {ins.name}')

        # Each Basic block has a list of incoming and outgoing basic blocks
        # A basic block can be shared by different functions
        # And the list of incoming/outgoing basic blocks depends of the function
        # incoming_basic_blocks(function_key) returns the list for the given function
        print('\t\tIncoming basic_block:')
        for incoming_bb in sorted(basic_block.incoming_basic_blocks(function.key), key=lambda x:x.start.pc):
            print(f'\t\t- {incoming_bb}')

        print('\t\tOutgoing basic_block:')
        for outgoing_bb in sorted(basic_block.outgoing_basic_blocks(function.key), key=lambda x:x.start.pc):
            print(f'\t\t- {outgoing_bb}')
