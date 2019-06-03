class BasicBlock(object):

    def __init__(self):
        self._instructions = []
        # incoming_basic_blocks and outgoing_basic_blocks are dict
        # The key is the function hash
        # It allows to compute the VSA only
        # On a specific function, to separate
        # the merging
        self._incoming_basic_blocks = {}
        self._outgoing_basic_blocks = {}

        # List of function keys that reaches the BB
        self.reacheable = []

    def add_instruction(self, instruction):
        self._instructions.append(instruction)

    def __repr__(self):
        return '<cfg BasicBlock@{:x}-{:x}>'.format(self.start.pc, self.end.pc)

    @property
    def start(self):
        '''First instruction of the basic block.'''
        return self._instructions[0]

    @property
    def end(self):
        '''Last instruction of the basic block.'''
        return self._instructions[-1]

    @property
    def instructions(self):
        return list(self._instructions)

    def incoming_basic_blocks(self, key):
        return self._incoming_basic_blocks.get(key, [])

    def outgoing_basic_blocks(self, key):
        return self._outgoing_basic_blocks.get(key, [])

    @property
    def incoming_basic_blocks_as_dict(self):
        return self._incoming_basic_blocks

    @property
    def outgoing_basic_blocks_as_dict(self):
        return self._outgoing_basic_blocks

    @property
    def all_incoming_basic_blocks(self):
        bbs = self._incoming_basic_blocks.values()
        bbs = [bb for sublist in bbs for bb in sublist]
        return list(set(bbs))

    @property
    def all_outgoing_basic_blocks(self):
        bbs = self._outgoing_basic_blocks.values()
        bbs = [bb for sublist in bbs for bb in sublist]
        return list(set(bbs))

    def add_incoming_basic_block(self, father, key):
        if not key in self._incoming_basic_blocks:
            self._incoming_basic_blocks[key] = []
        if father not in self._incoming_basic_blocks[key]:
            self._incoming_basic_blocks[key].append(father)

    def add_outgoing_basic_block(self, son, key):
        if not key in self._outgoing_basic_blocks:
            self._outgoing_basic_blocks[key] = []
        if son not in self._outgoing_basic_blocks[key]:
            self._outgoing_basic_blocks[key].append(son)

    def ends_with_jumpi(self):
        return self.end.name == 'JUMPI'

    def ends_with_jump_or_jumpi(self):
        return self.end.name in ('JUMP', 'JUMPI')

    def true_branch(self, key):
        assert(self.ends_with_jumpi())

        outgoing_basic_blocks = [
            bb for bb in self.outgoing_basic_blocks(key)
            if bb.start.pc != self.end.pc + 1
        ]

        if len(outgoing_basic_blocks[key]) > 1:
            return

        return next(outgoing_basic_blocks[key], None)

    def false_branch(self, key):
        assert(self.ends_with_jumpi())

        outgoing_basic_blocks = [
            bb for bb in self.outgoing_basic_blocks(key)
            if bb.start.pc == self.end.pc + 1
        ]
        if len(outgoing_basic_blocks) > 1:
            return

        return next(outgoing_basic_blocks[key], None)

