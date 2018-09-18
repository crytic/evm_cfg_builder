BASIC_BLOCK_END = ['STOP',
                   'SELFDESTRUCT',
                   'RETURN',
                   'REVERT',
                   'INVALID',
                   'SUICIDE',
                   'JUMP',
                   'JUMPI']


def create_dicts_from_basic_blocks(basic_blocks):
    """
        Create two dict:
            - pc -> basic block. PC is either the start or the end of the BB
            - pc -> node

    Args:
        list(BasicBlock)
    Returns
        dict(int-> BasicBlock), dict(int->Instruction)
    """
    nodes_as_dict = {}
    basic_blocks_as_dict = {}

    for bb in basic_blocks:
        basic_blocks_as_dict[bb.start.pc] = bb
        basic_blocks_as_dict[bb.end.pc] = bb
        for ins in bb.instructions:
            nodes_as_dict[ins.pc] = ins
    return (basic_blocks_as_dict, nodes_as_dict)
