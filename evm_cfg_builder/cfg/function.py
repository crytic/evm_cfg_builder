import logging
logger = logging.getLogger("evm-cfg-builder")

class Function(object):

    DISPATCHER_ID = -2
    FALLBACK_ID = -1

    def __init__(self, hash_id, start_addr, entry_basic_block, cfg):
        self._hash_id = hash_id
        self._start_addr = start_addr
        self._entry = entry_basic_block
        if hash_id == self.FALLBACK_ID:
            self.name = '_fallback'
        elif hash_id == Function.DISPATCHER_ID:
            self.name = '_dispatcher'
        else:
            self._name = hex(hash_id)
        self._basic_blocks = []
        self._attributes = []
        self._cfg = cfg

    @property
    def start_addr(self):
        return self._start_addr

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
        attrs = ''
        if self.attributes:
            attrs = ", " + ",".join(self.attributes)
        return '{}, {} #bbs {}'.format(self.name, len(self.basic_blocks), attrs)

    def output_to_dot(self, base_filename):

        if self.key == Function.DISPATCHER_ID:
            self.output_dispatcher_to_dot(base_filename)
            return

        with open('{}{}.dot'.format(base_filename, self.name), 'w') as f:
            f.write('digraph{\n')
            for basic_block in self.basic_blocks:
                instructions = ['{}:{}'.format(hex(ins.pc),
                                               str(ins)) for ins in basic_block.instructions]
                instructions = '\n'.join(instructions)

                f.write('{}[label="{}"]\n'.format(basic_block.start.pc, instructions))

                if self.key in basic_block.incoming_basic_blocks_as_dict:
                    for son in basic_block.incoming_basic_blocks_as_dict[self.key]:
                        f.write('{} -> {}\n'.format(basic_block.start.pc, son.start.pc))

                elif basic_block.ends_with_jump_or_jumpi():
                    logger.error('Missing branches {}:{}'.format(self.name,
                                                                 hex(basic_block.end.pc)))

            f.write('\n}')

    def output_dispatcher_to_dot(self, base_filename):

        destinations = {function.hash_id : function.start_addr for function in self._cfg.functions}

        with open('{}{}.dot'.format(base_filename, self.name), 'w') as f:
            f.write('digraph{\n')
            for basic_block in self.basic_blocks:
                instructions = ['{}:{}'.format(hex(ins.pc),
                                               str(ins)) for ins in basic_block.instructions]
                instructions = '\n'.join(instructions)

                f.write('{}[label="{}"]\n'.format(basic_block.start.pc, instructions))

                if self.key in basic_block.incoming_basic_blocks_as_dict:
                    for son in basic_block.incoming_basic_blocks_as_dict[self.key]:
                        f.write('{} -> {}\n'.format(basic_block.start.pc, son.start.pc))

                elif basic_block.ends_with_jump_or_jumpi():
                    logger.error('Missing branches {}:{}'.format(self.name,
                                                                 hex(basic_block.end.pc)))
            for function in self._cfg.functions:
                if function != self:
                    f.write('{}[label="Call {}"]\n'.format(function.start_addr, function.name))

            f.write('\n}')

