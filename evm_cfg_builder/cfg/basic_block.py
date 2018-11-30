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

        # List of function keys that reaches the BB
        self.reacheable = []

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
        if father not in self.fathers[key]:
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
