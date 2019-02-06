from .basic_block import BasicBlock
from .function import Function

__all__ = ["CFG", "BasicBlock", "Function"]

from ..known_hashes import known_hashes
from ..value_set_analysis import StackValueAnalysis

import re
from pyevmasm import disassemble_all, Instruction

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

class CFG(object):
    """Implements the control flow graph (CFG) of an EVM bytecode.
    """

    def __init__(self, bytecode: bytes=None):
        """Initialize an EVM CFG.

        :param bytecode: The EVM bytecode
        :type bytecode: None, bytes
        """
        self._functions = dict()
        # __basic_blocks is a dict that matches
        # an address to the basic block
        # The address can be the first or the last
        # instructions 
        self._basic_blocks = dict()
        self._instructions = dict()

        assert(isinstance(bytecode, (type(None), bytes)))

        self._bytecode = bytecode
        self._analysis_complete = False

    @classmethod
    def from_byte_str(cls, bytecode: str) -> cls:
        return cls(bytes(bytecode.encode('charmap')))

    @classmethod
    def from_hex_str(cls, bytecode: str) -> cls:
        bytecode = bytes.fromhex(bytecode[2:])
        return cls(bytecode)

    @classmethod
    def from_bytes(cls, bytecode: bytes) -> cls:
        return cls(bytecode)

    @classmethod
    def from_hex_bytes(cls, bytecode: bytes) -> cls:
        return cls(bytes.fromhex(bytecode[2:].decode()))

    @property
    def analysis_complete(self) -> bool:
        return self._analysis_complete

    def __repr__(self) -> str:
        return "<CFG: {} Functions, {} Basic Blocks>".format(
            len(self.functions),
            len(self.basic_blocks)
        )

    @property
    def bytecode(self) -> bytes:
        return self._bytecode

    @property
    def basic_blocks(self) -> list:
        '''
        Return the list of basic_block
        '''
        bbs = self._basic_blocks.values()
        return list(set(bbs))

    @property
    def entry_point(self) -> BasicBlock:
        '''
        Return the entry point of the cfg (the basic block at 0x0)
        '''
        return self._basic_blocks[0]

    @property
    def functions(self) -> list:
        '''
        Return the list of functions
        '''
        return list(self._functions.values())

    @property
    def instructions(self) -> list:
        '''
        Return the list of instructions
        '''
        return list(self._instructions.values())

    def get_instruction_at(self, addr: int) -> Instruction:
        '''Return the instruction at the provided address.

        :param addr: Address of instruction
        :type addr: int
        '''
        return self._instructions.get(addr)

    def get_basic_block_at(self, addr: int) -> BasicBlock:
        '''Return the basic block at the provided address.

        The address is either the starting or ending instruction of the
        basic block.

        :param addr: Address of basic block start or end
        :type addr: int
        :return: BasicBlock, None -- the requested basic block
        '''
        return self._basic_blocks.get(addr)

    def get_function_at(self, addr: int) -> Function:
        '''Return the function at the provided address.

        :param addr: Address of the function
        :type addr: int
        :return: Function, None -- the requested function
        '''
        return self._functions.get(addr)

    def analyze(self):
        self.compute_basic_blocks()

        if self._basic_blocks:
            self.compute_functions(self._basic_blocks[0], True)
            self.add_function(Function(Function.DISPATCHER_ID, 0, self._basic_blocks[0], self))

        for function in self.functions:
            if function.hash_id in known_hashes:
                function.name = known_hashes[function.hash_id]

            vsa = StackValueAnalysis(
                self,
                function.entry,
                function.hash_id
            )
            bbs = vsa.analyze()

            function.basic_blocks = [self._basic_blocks[bb] for bb in bbs]

            if function.hash_id != Function.DISPATCHER_ID:
                function.check_payable()
                function.check_view()
                function.check_pure()

        self._analysis_complete = True

    def clear(self):
        self._functions = dict()
        self._basic_blocks = dict()
        self._instructions = dict()
        self._bytecode = bytes()
        self._analysis_complete = False

    def remove_metadata(self):
        '''
            Init bytecode contains metadata that needs to be removed
            see http://solidity.readthedocs.io/en/v0.4.24/metadata.html#encoding-of-the-metadata-hash-in-the-bytecode
        '''
        if self._bytecode is None:
            return

        self.bytecode = re.sub(
            bytes(r'\xa1\x65\x62\x7a\x7a\x72\x30\x58\x20[\x00-\xff]{32}\x00\x29'.encode('charmap')),
            b'',
            self.bytecode
        )

    def compute_basic_blocks(self):
        '''
            Split instructions into BasicBlock
        Args:
            self: CFG
        Returns:
            None
        '''
        # Do nothing if bytecode is None
        if self._bytecode is None:
            return

        # Do nothing if basic_blocks already exists
        if self._basic_blocks:
            return

        bb = BasicBlock()

        for instruction in disassemble_all(self.bytecode):
            self._instructions[instruction.pc] = instruction

            if instruction.name == 'JUMPDEST':
                # JUMPDEST indicates a new BasicBlock. Set the end pc
                # of the current block, and switch to a new one.
                if bb._instructions:
                    self._basic_blocks[bb.end.pc] = bb

                bb = BasicBlock()

                self._basic_blocks[instruction.pc] = bb

            bb.add_instruction(instruction)

            if bb.start.pc == instruction.pc:
                self._basic_blocks[instruction.pc] = bb

            if bb.end.name in BASIC_BLOCK_END:
                self._basic_blocks[bb.end.pc] = bb
                bb = BasicBlock()

    def compute_functions(self, block: BasicBlock, is_entry_block:bool=False):
        function_start, function_hash = is_jump_to_function(block)

        if(function_start):
            new_function = Function(
                function_hash,
                function_start,
                self._basic_blocks[function_start],
                self
            )

            self._functions[function_start] = new_function

            if block.ends_with_jumpi():
                false_branch = self._basic_blocks[block.end.pc + 1]
                self.compute_functions(false_branch)

            return

        elif is_entry_block:
            if block.ends_with_jumpi():
                false_branch = self._basic_blocks[block.end.pc + 1]
                self.compute_functions(false_branch)

    def add_function(self, func: Function):
        assert isinstance(func, Function)
        self._functions[func._start_addr] = func

    def compute_simple_edges(self, key):
        for bb in self._basic_blocks.values():

            if bb.end.name == 'JUMPI':
                dst = self._basic_blocks[bb.end.pc + 1]
                bb.add_outgoing_basic_block(dst, key)
                dst.add_incoming_basic_block(bb, key)

            # A bb can be split in the middle if it has a JUMPDEST
            # Because another edge can target the JUMPDEST
            if bb.end.name not in BASIC_BLOCK_END:
                try:
                    dst = self._basic_blocks[bb.end.pc + 1 + bb.end.operand_size]
                except KeyError:
                    continue
                assert dst.start.name == 'JUMPDEST'
                bb.add_outgoing_basic_block(dst, key)
                dst.add_incoming_basic_block(bb, key)

    def compute_reachability(self, entry_point: int, key):
        bbs_saw = [entry_point]

        bbs_to_explore = [entry_point]
        while bbs_to_explore:
            bb = bbs_to_explore.pop()
            for son in bb.outgoing_basic_blocks(key):
                if not son in bbs_saw:
                    bbs_saw.append(son)
                    bbs_to_explore.append(son)

        for bb in bbs_saw:
            bb.reacheable.append(key)

        # clean son/fathers that are created by compute_simple_edges
        # but are not reacheable
        for bb in self._basic_blocks.values():
            if not bb in bbs_saw:
                if key in bb._incoming_basic_blocks:
                    bb._incoming_basic_blocks.pop(key)
                if key in bb._outgoing_basic_blocks:
                    bb._outgoing_basic_blocks.pop(key)

    def output_to_dot(self, base_filename: str):

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

def is_jump_to_function(block: BasicBlock) -> bool:
    '''
        Heuristic:
        Recent solc version add a first check if calldatasize <4 and jump in fallback
    Args:
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
