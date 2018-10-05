import binascii
import re
import sys

from pyevmasm import disassemble_all

from .cfg import compute_instructions, find_functions, Function
from .evm_helpers import create_dicts_from_basic_blocks
from .known_hashes import known_hashes
from .value_set_analysis import StackValueAnalysis

DISPATCHER_ID = -2
FALLBACK_ID = -1


def remove_metadata(bytecode):
    '''
        Init bytecode contains metadata that needs to be removed
        see http://solidity.readthedocs.io/en/v0.4.24/metadata.html#encoding-of-the-metadata-hash-in-the-bytecode
    '''
    return re.sub(
        r'\xa1\x65\x62\x7a\x7a\x72\x30\x58\x20[\x00-\xff]{32}\x00\x29',
        '',
        bytecode
    )


def get_info(bytecode):
    instructions = disassemble_all(bytecode)
    basic_blocks = compute_instructions(instructions)
    basic_blocks_as_dict, nodes_as_dict = create_dicts_from_basic_blocks(
        basic_blocks
    )

    functions = find_functions(basic_blocks[0], basic_blocks_as_dict, True)
    dispatcher = Function(-2, 0, basic_blocks_as_dict[0])
    functions = [dispatcher] + functions

    for function in functions:
        if function.hash_id == FALLBACK_ID:
            function.name = '_fallback'
        elif function.hash_id == DISPATCHER_ID:
            function.name = '_dispatcher'
        else:
            if function.hash_id in known_hashes:
                function.name = known_hashes[function.hash_id]

    for function in functions:
        vsa = StackValueAnalysis(
            function.entry,
            basic_blocks_as_dict,
            nodes_as_dict,
            function.hash_id
        )
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
        bytecode = binascii.unhexlify(bytecode)
        bytecode = remove_metadata(bytecode)
        functions = get_info(bytecode)
        print('End of analysis')
        for function in functions:
            print(function)
        output_to_dot(functions)


if __name__ == '__main__':
    main()
