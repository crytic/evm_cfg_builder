import sys
import re
import binascii

from pyevmasm import disassemble_all
from evm_helpers import create_dicts_from_basic_blocks
from known_hashes import knownHashes


from value_set_analysis import StackValueAnalysis
from cfg import compute_instructions, find_functions

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
    instructions = list(disassemble_all(binascii.unhexlify(bytecode))) # TODO allow raw bytecode
    basic_blocks = compute_instructions(instructions)
    (basic_blocks_as_dict, nodes_as_dict) = create_dicts_from_basic_blocks(basic_blocks)

    functions = find_functions(basic_blocks[0], basic_blocks_as_dict, True)

    for function in functions:
        h = hex(function.hash_id)
        if h in knownHashes:
            function.name = knownHashes[h]

    for function in functions:
        print('Analyze {}'.format(function.name))
        vsa = StackValueAnalysis(function.entry, basic_blocks_as_dict, nodes_as_dict, function.hash_id)
        bbs = vsa.analyze()
        function.basic_blocks = [basic_blocks_as_dict[bb] for bb in bbs]

        function.check_payable()
        function.check_view()
        function.check_pure()


    print('End of analysis')

    for function in functions:
        print(function)
    output_to_dot(functions)

def output_to_dot(functions):
    for function in functions:
        function.output_to_dot('test_')

if __name__ == '__main__':

    filename = sys.argv[1]

    with open(filename) as f:
        get_info(f.read().replace('\n',''))
