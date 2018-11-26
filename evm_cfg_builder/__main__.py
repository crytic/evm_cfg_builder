import binascii
import re
import sys

from pyevmasm import disassemble_all

from .cfg import CFG
from .cfg.function import Function
from .known_hashes import known_hashes
from .value_set_analysis import StackValueAnalysis

DISPATCHER_ID = -2
FALLBACK_ID = -1


def get_info(cfg):
    cfg.add_function(Function(DISPATCHER_ID, 0, cfg.basic_blocks[0]))

    for function in cfg.functions:
        if function.hash_id == FALLBACK_ID:
            function.name = '_fallback'
        elif function.hash_id == DISPATCHER_ID:
            function.name = '_dispatcher'
        else:
            if function.hash_id in known_hashes:
                function.name = known_hashes[function.hash_id]

    for function in cfg.functions:
        vsa = StackValueAnalysis(
            cfg,
            function.entry,
            function.hash_id
        )
        bbs = vsa.analyze()

        function.basic_blocks = [cfg.basic_blocks[bb] for bb in bbs]

        function.check_payable()
        function.check_view()
        function.check_pure()

def output_to_dot(functions):
    for function in functions:
        function.output_to_dot('test_')

def main():
    filename = sys.argv[1]

    with open(filename) as f:
        bytecode = f.read().replace('\n','')
        cfg = CFG(binascii.unhexlify(bytecode))
        cfg.remove_metadata()
        cfg.compute_basic_blocks()
        cfg.compute_functions(cfg.basic_blocks[0], True)
        get_info(cfg)
        print('End of analysis')
        for function in cfg.functions:
            print(function)
        output_to_dot(cfg.functions)


if __name__ == '__main__':
    main()
