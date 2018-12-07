import binascii
from . import basic_block
from .function import Function

from ..known_hashes import known_hashes
from ..value_set_analysis import StackValueAnalysis

import re
from pyevmasm import disassemble_all

__all__ = ["basic_block", "function"]

BASIC_BLOCK_END = [
    'STOP',
    'SELFDESTRUCT',
    'RETURN',
    'REVERT',
    'INVALID',
    'SUICIDE',
    'JUMP',
    'JUMPI'
]

class ImmutableDict(dict):
    def __init__(self, map):
        self.update(map)
        self.update = self.__update

    def __setitem__(self, key, value):
        raise KeyError('ImmutableDict is immutable.')

    def __update(self, new_dict):
        raise NotImplementedError()

class CFG(object):

    def __init__(self, bytecode=None, instructions=None, basic_blocks=None, functions=None, remove_metadata=True, analyze=True):
        self.__functions = list()
        # __basic_blocks is a dict that matches
        # an address to the basic block
        # The address can be the first or the last
        # instructions 
        self.__basic_blocks = dict()
        self.__instructions = dict()

        if bytecode is not None:
            if isinstance(bytecode, str):
                if bytecode.startswith('0x'):
                    bytecode = bytecode[2:]
                bytecode = bytecode.replace('\n', '')
                bytecode = binascii.unhexlify(bytecode)
            self.__bytecode = bytes(bytecode)
            if instructions is not None:
                self.__instructions = instructions
                if basic_blocks is not None:
                    self.__basic_blocks = basic_blocks
                    if functions is not None:
                        self.__functions = functions

        if remove_metadata:
            self.remove_metadata()
        if analyze:
            self.analyze()

    def analyze(self):
        self.compute_basic_blocks()
        self.compute_functions(self.__basic_blocks[0], True)
        self.add_function(Function(Function.DISPATCHER_ID, 0, self.__basic_blocks[0], self))

        for function in self.functions:
            if function.hash_id in known_hashes:
                function.name = known_hashes[function.hash_id]

        for function in self.functions:
            vsa = StackValueAnalysis(
                self,
                function.entry,
                function.hash_id
            )
            bbs = vsa.analyze()

            function.basic_blocks = [self.__basic_blocks[bb] for bb in bbs]

            if function.hash_id != Function.DISPATCHER_ID:
                function.check_payable()
                function.check_view()
                function.check_pure()



    @property
    def bytecode(self):
        return self.__bytecode

    @bytecode.setter
    def bytecode(self, bytecode):
        self.clear()
        self.__bytecode = bytecode

    def clear(self):
        self.__functions = list()
        self.__basic_blocks = dict()
        self.__instructions = dict()
        self.__bytecode = dict()

    def remove_metadata(self):
        '''
            Init bytecode contains metadata that needs to be removed
            see http://solidity.readthedocs.io/en/v0.4.24/metadata.html#encoding-of-the-metadata-hash-in-the-bytecode
        '''
        self.bytecode = re.sub(
            bytes(r'\xa1\x65\x62\x7a\x7a\x72\x30\x58\x20[\x00-\xff]{32}\x00\x29'.encode('charmap')),
            b'',
            self.bytecode
        )

    @property
    def basic_blocks(self):
        '''
        Return an iterator of basic_block
        '''
        bbs = self.__basic_blocks.values()
        return iter(iter(set(bbs)))

    @property
    def functions(self):
        '''
        Return an iterator of functions
        '''
        return iter(self.__functions)

    @property
    def instructions(self):
        '''
        Return an iterator of instructions
        '''
        return iter(self.__instructions.values())

    @property
    def basic_blocks_from_addr(self):
        '''
        Return a dict that match an addr to a BB
        The addr can be the first or the last ins of the BB
        returns:
            ImmutableDict
        '''
        return ImmutableDict(self.__basic_blocks)

    @property
    def instructions_from_addr(self):
        '''
        Return a dict that match an addr to a instruction
        returns:
            ImmutableDict
        '''
        return ImmutableDict(self.__instructions)

    def compute_basic_blocks(self):
        '''
            Split instructions into BasicBlock
        Args:
            self: CFG
        Returns:
            None
        '''
        # Do nothing if basic_blocks already exist
        if self.__basic_blocks:
            return

        bb = basic_block.BasicBlock()

        for instruction in disassemble_all(self.bytecode):
            self.__instructions[instruction.pc] = instruction

            if instruction.name == 'JUMPDEST':
                # JUMPDEST indicates a new BasicBlock. Set the end pc
                # of the current block, and switch to a new one.
                if bb.instructions:
                    self.__basic_blocks[bb.end.pc] = bb

                bb = basic_block.BasicBlock()

                self.__basic_blocks[instruction.pc] = bb

            bb.add_instruction(instruction)

            if bb.start.pc == instruction.pc:
                self.__basic_blocks[instruction.pc] = bb

            if bb.end.name in BASIC_BLOCK_END:
                self.__basic_blocks[bb.end.pc] = bb
                bb = basic_block.BasicBlock()

    def compute_functions(self, block, is_entry_block=False):

        function_start, function_hash = is_jump_to_function(block)

        if(function_start):
            new_function = Function(
                function_hash,
                function_start,
                self.__basic_blocks[function_start],
                self
            )

            self.__functions.append(new_function)

            if block.ends_with_jumpi():
                false_branch = self.__basic_blocks[block.end.pc + 1]
                self.compute_functions(false_branch)

            return

        elif is_entry_block:
            if block.ends_with_jumpi():
                false_branch = self.__basic_blocks[block.end.pc + 1]
                self.compute_functions(false_branch)

    def add_function(self, func):
        assert isinstance(func, Function)
        self.__functions.append(func)

    def compute_simple_edges(self, key):
        for bb in self.__basic_blocks.values():

            if bb.end.name == 'JUMPI':
                dst = self.__basic_blocks[bb.end.pc + 1]
                bb.add_incoming_basic_block(dst, key)
                dst.add_outgoing_basic_block(bb, key)

            # A bb can be split in the middle if it has a JUMPDEST
            # Because another edge can target the JUMPDEST
            if bb.end.name not in BASIC_BLOCK_END:
                try:
                    dst = self.__basic_blocks[bb.end.pc + 1 + bb.end.operand_size]
                except KeyError:
                    continue
                assert dst.start.name == 'JUMPDEST'
                bb.add_incoming_basic_block(dst, key)
                dst.add_outgoing_basic_block(bb, key)

    def compute_reachability(self, entry_point, key):
        bbs_saw = [entry_point]

        bbs_to_explore = [entry_point]
        while bbs_to_explore:
            bb = bbs_to_explore.pop()
            for son in bb.incoming_basic_blocks(key):
                if not son in bbs_saw:
                    bbs_saw.append(son)
                    bbs_to_explore.append(son)

        for bb in bbs_saw:
            bb.reacheable.append(key)

        # clean son/fathers that are created by compute_simple_edges
        # but are not reacheable
        for bb in self.__basic_blocks.values():
            if not bb in bbs_saw:
                if key in bb.incoming_basic_blocks_as_dict.keys():
                    del bb.incoming_basic_blocks_as_dict[key]
                if key in bb.outgoing_basic_blocks_as_dict.keys():
                    del bb.outgoing_basic_blocks_as_dict[key]

    def output_to_dot(self, base_filename):

        with open('{}{}.dot'.format(base_filename, 'FULL_GRAPH'), 'w') as f:
            f.write('digraph{\n')
            for basic_block in self.basic_blocks:
                instructions = ['{}:{}'.format(hex(ins.pc),
                                               str(ins)) for ins in basic_block.instructions]
                instructions = '\n'.join(instructions)

                f.write('{}[label="{}"]\n'.format(basic_block.start.pc, instructions))

                for son in basic_block.all_incoming_basic_blocks:
                    f.write('{} -> {}\n'.format(basic_block.start.pc, son.start.pc))

            f.write('\n}')

def is_jump_to_function(block):
    '''
        Heuristic:
        Recent solc version add a first check if calldatasize <4 and jump in fallback
    Args;
        block (BasicBlock)
    Returns:
        (int): function hash, or None
    '''

    has_calldata_size = False
    last_pushed_value = None
    previous_last_pushed_value = None
    for i in block.instructions:
        if i.name == 'CALLDATASIZE':
            has_calldata_size = True

        if i.name.startswith('PUSH'):
            previous_last_pushed_value = last_pushed_value
            last_pushed_value = i.operand

    if i.name == 'JUMPI' and has_calldata_size:
        return last_pushed_value, -1

    if i.name == 'JUMPI' and previous_last_pushed_value:
        return last_pushed_value, previous_last_pushed_value

    return None, None
