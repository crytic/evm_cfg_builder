import binascii
import re
import sys

from pyevmasm import disassemble_all

from .cfg import compute_instructions, find_functions
from .evm_helpers import create_dicts_from_basic_blocks
from .known_hashes import known_hashes
from .value_set_analysis import StackValueAnalysis


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

    instructions = disassemble_all(bytecode)
    basic_blocks = compute_instructions(instructions)
    (basic_blocks_as_dict, nodes_as_dict) = create_dicts_from_basic_blocks(basic_blocks)

    functions = find_functions(basic_blocks[0], basic_blocks_as_dict, True)

    for function in functions:
        if function.hash_id == -1:
            function.name = '_fallback'
        else:
            if function.hash_id in known_hashes:
                function.name = known_hashes[function.hash_id]

    for function in functions:
        #print('Analyze {}'.format(function.name))
        vsa = StackValueAnalysis(function.entry, basic_blocks_as_dict, nodes_as_dict, function.hash_id)
        bbs = vsa.analyze()
        function.basic_blocks = [basic_blocks_as_dict[bb] for bb in bbs]

        function.check_payable()
        function.check_view()
        function.check_pure()

    return functions

def output_to_dot(functions):
    for function in functions:
        function.output_to_dot('test_')

def main():
    filename = sys.argv[1]

    with open(filename) as f:
        bytecode = f.read().replace('\n','')
        bytecode = remove_metadata(bytecode)
        bytecode = binascii.unhexlify(bytecode)
        functions = get_info(bytecode)
        print('End of analysis')
        for function in functions:
            print(function)
        output_to_dot(functions)


if __name__ == '__main__':
    main()
