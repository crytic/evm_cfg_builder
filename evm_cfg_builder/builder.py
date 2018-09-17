import sys
import re
import binascii

from pyevmasm import disassemble_all

from value_set_analysis import StackValueAnalysis
from cfg import split_instructions, find_functions

def remove_metadata(bytecode):
    '''
        Init bytecode contains metadata that needs to be removed
        see http://solidity.readthedocs.io/en/v0.4.24/metadata.html#encoding-of-the-metadata-hash-in-the-bytecode
    '''
    if len(bytecode) < 86:
        return bytecode

    metadata = bytecode[-86::]
    if re.match('a165627a7a72305820[0-9a-z]{64}0029', metadata):
        return bytecode[:-86]
    return bytecode


def get_info(bytecode):

    bytecode = remove_metadata(bytecode)
    instructions = list(disassemble_all(binascii.unhexlify(bytecode))) # todo use generator
    basic_blocks = split_instructions(instructions)

    vsa = StackValueAnalysis(basic_blocks)
    vsa.analyze()

    find_functions(basic_blocks[0], True)

    output_to_dot(basic_blocks)

def output_to_dot(basic_blocks):
    with open('test.dot', 'w') as f:
        f.write('digraph{\n')

        for basic_block in basic_blocks:
            instructions = ['{}:{}'.format(hex(ins.pc), str(ins)) for ins in basic_block.instructions]
            instructions = '\n'.join(instructions)
            f.write('{}[label="{}"]\n'.format(basic_block.start.pc, instructions))
            for son in basic_block.sons:
                f.write('{} -> {}\n'.format(basic_block.start.pc, son.start.pc))
        f.write('\n}')



if __name__ == '__main__':

    filename = sys.argv[1]

    with open(filename) as f:
        get_info(f.read().replace('\n',''))
