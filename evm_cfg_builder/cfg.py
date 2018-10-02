from .evm_helpers import BASIC_BLOCK_END

class BasicBlock(object):

    def __init__(self):
        self.instructions = []
        # sons and fathers are dict
        # The key is the function hash
        # It allows to compute the VSA only
        # On a specific function, to separate
        # the merging
        self.sons = {}
        self.fathers = {}

    def add_instruction(self, instruction):
        self.instructions += [instruction]

    def __repr__(self):
        return '<cfg BasicBlock@{:x}-{:x}>'.format(self.start.pc, self.end.pc)

    @property
    def start(self):
        return self.instructions[0]

    @property
    def end(self):
        return self.instructions[-1]


    def add_son(self, son, key):
        if not key in self.sons:
            self.sons[key] = []
        if son not in self.sons[key]:
            self.sons[key].append(son)

    def add_father(self, father, key):
        if not key in self.fathers:
            self.fathers[key] = []
        if father not in self.fathers:
            self.fathers[key].append(father)

    def ends_with_jumpi(self):
        return self.end.name == 'JUMPI'

    def ends_with_jump_or_jumpi(self):
        return self.end.name in ['JUMP', 'JUMPI']

    def true_branch(self, key):
        assert(self.ends_with_jumpi())

        sons = [bb for bb in self.sons[key] if bb.start.pc != (self.end.pc+1)]
        assert(len(sons[key]) == 1)
        return sons[key][1]

    def false_branch(self, key):
        assert(self.ends_with_jumpi())

        sons = [bb for bb in self.sons[key] if bb.start.pc == (self.end.pc+1)]
        assert(len(sons) == 1)
        return sons[key][0]

class Function(object):

    def __init__(self, hash_id, start_addr, entry_basic_block):
        self._hash_id = hash_id
        self._start_addr = start_addr
        self._entry = entry_basic_block
        self._name = hex(hash_id)
        self._basic_blocks = []
        self._attributes = []

    @property
    def hash_id(self):
        return self._hash_id

    @property
    def key(self):
        return self.hash_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def basic_blocks(self):
        '''
        Returns
            list(BasicBlock)
        '''
        return self._basic_blocks

    @basic_blocks.setter
    def basic_blocks(self, bbs):
        self._basic_blocks = bbs

    @property
    def entry(self):
        return self._entry

    @property
    def attributes(self):
        """
        Returns
            list(str)
        """
        return self._attributes

    def add_attributes(self, attr):
        if not attr in self.attributes:
            self._attributes.append(attr)

    def check_payable(self):
        entry = self.entry
        if any(ins.name == 'CALLVALUE' for ins in entry.instructions):
            return
        self.add_attributes('payable')

    def check_view(self):
        changing_state_ops = ['CREATE',
                              'CALL',
                              'CALLCODE',
                              'DELEGATECALL',
                              'SELFDESTRUCT',
                              'SSTORE']

        for bb in self.basic_blocks:
            if any(ins.name in changing_state_ops for ins in bb.instructions):
                return

        self.add_attributes('view')

    def check_pure(self):
        state_ops = ['CREATE',
                     'CALL',
                     'CALLCODE',
                     'DELEGATECALL',
                     'SELFDESTRUCT',
                     'SSTORE',
                     'ADDRESS',
                     'BALANCE',
                     'ORIGIN',
                     'CALLER',
                     'CALLVALUE',
                     'CALLDATALOAD',
                     'CALLDATASIZE',
                     'CALLDATACOPY'
                     'CODESIZE',
                     'CODECOPY',
                     'EXTCODESIZE',
                     'EXTCODECOPY',
                     'RETURNDATASIZE',
                     'RETURNDATACOPY',
                     'BLOCKHASH',
                     'COINBASE',
                     'TIMESTAMP',
                     'NUMBER',
                     'DIFFICULTY',
                     'GASLIMIT',
                     'LOG0', 'LOG1', 'LOG2', 'LOG3', 'LOG4',
                     'CREATE',
                     'CALL',
                     'CALLCODE',
                     'DELEGATECALL',
                     'STATICCALL',
                     'SELFDESTRUCT',
                     'SSTORE',
                     'SLOAD']

        for bb in self.basic_blocks:
            if any(ins.name in state_ops for ins in bb.instructions):
                return

        self.add_attributes('pure')

    def __str__(self):
        attrs  = ''
        if self.attributes:
            attrs = ", " + ",".join(self.attributes)
        return '{}, {} #bbs {}'.format(self.name, len(self.basic_blocks), attrs)

    def output_to_dot(self, base_filename):

        with open('{}{}.dot'.format(base_filename, self.name), 'w') as f:
            f.write('digraph{\n')
            for basic_block in self.basic_blocks:
                instructions = ['{}:{}'.format(hex(ins.pc),
                                               str(ins)) for ins in basic_block.instructions]
                instructions = '\n'.join(instructions)

                f.write('{}[label="{}"]\n'.format(basic_block.start.pc, instructions))

                if self.key in basic_block.sons:
                    for son in basic_block.sons[self.key]:
                        f.write('{} -> {}\n'.format(basic_block.start.pc, son.start.pc))

                elif basic_block.ends_with_jump_or_jumpi():
                    print('Missing branches {}:{}'.format(self.name,
                                                          hex(basic_block.end.pc)))

            f.write('\n}')

def compute_instructions(instructions):
    '''
        Split instructions into BasicBlock
        Update PC of instructions
    Args:
        list(Instruction)
    Returns:
        list(BasicBlocks)
    '''
    bbs = []
    bb = BasicBlock()

    addr = 0
    for instruction in instructions:
        instruction.pc = addr
        addr += instruction.operand_size + 1
        # JUMPDEST can be preceded by a no-jump instruction
        if instruction.name == 'JUMPDEST':
            if bb.instructions:
                bbs.append(bb)

            bb = BasicBlock()
            bb.add_instruction(instruction)
        else:
            bb.add_instruction(instruction)
            if instruction.name in BASIC_BLOCK_END:
                bbs.append(bb)
                bb = BasicBlock()

    return bbs

def is_jump_to_function(block):
    '''
        Heuristic: 
        Recent solc version add a first check if calldatasize <4 and jump in fallback
    Args;
        block (BasicBlock)
    Returns:
        (int): function hash, or None
    '''

    has_calldata_load = False
    last_pushed_value = None
    previous_last_pushed_value = None
    for i in block.instructions:

        #print(hex(i.pc))
        if i.name.startswith('PUSH'):
            previous_last_pushed_value = last_pushed_value
            last_pushed_value = i.operand

    if i.name == 'JUMPI' and previous_last_pushed_value:
        return last_pushed_value, previous_last_pushed_value
    return None, None

def find_functions(block, basic_block_as_dict, is_entry_block=False):

    function_start, function_hash = is_jump_to_function(block)

    if(function_start):
 #       print('Function {} starts at {}'.format(hex(function_hash), hex(function_start)))
#        function = {function_start: {'hash':function_hash, 'start_hex':hex(function_start)}}
        function = Function(function_hash, function_start, basic_block_as_dict[function_start])

        ret = {}
        if block.ends_with_jumpi():
            false_branch = basic_block_as_dict[block.end.pc + 1]
            ret = find_functions(false_branch, basic_block_as_dict)

#        false_branch = block.false_branch()
        return [function] + ret

    elif is_entry_block:
        if block.ends_with_jumpi():
            false_branch = basic_block_as_dict[block.end.pc + 1]
            return find_functions(false_branch, basic_block_as_dict)
#    else:
        #print('Last {}'.format(hex(block.start.pc)))
    return []


def add_simple_edges(basic_blocks, basic_blocks_as_dict):
    for bb in basic_blocks:
        if bb.end.name == 'JUMPI':
            dst = basic_blocks_as_dict[bb.end.pc + 1]
            bb.add_son(dst)
            dst.add_father(bb)
        # A bb can be split in the middle if it has a JUMPDEST
        # Because another edge can target the JUMPDEST
        if bb.end.name not in BASIC_BLOCK_END:
            dst = basic_blocks_as_dict[bb.end.pc + 1 + bb.end.operand_size]
            assert dst.start.name == 'JUMPDEST'
            bb.add_son(dst)
            dst.add_father(bb)
