from typing import List, Dict

from pyevmasm import Instruction


class BasicBlock:
    def __init__(self) -> None:
        self._instructions: List[Instruction] = []
        # incoming_basic_blocks and outgoing_basic_blocks are dict
        # The key is the function hash
        # It allows to compute the VSA only
        # On a specific function, to separate
        # the merging
        self._incoming_basic_blocks: Dict[int, List["BasicBlock"]] = {}
        self._outgoing_basic_blocks: Dict[int, List["BasicBlock"]] = {}

        # List of function keys that reaches the BB
        self.reacheable: List[int] = []

    def add_instruction(self, instruction: Instruction) -> None:
        self._instructions.append(instruction)

    def __repr__(self) -> str:
        return f"<cfg BasicBlock@{hex(self.start.pc)}-{hex(self.end.pc)}>"

    @property
    def start(self) -> Instruction:
        """First instruction of the basic block."""
        return self._instructions[0]

    @property
    def end(self) -> Instruction:
        """Last instruction of the basic block."""
        return self._instructions[-1]

    @property
    def instructions(self) -> List[Instruction]:
        return list(self._instructions)

    def incoming_basic_blocks(self, key: int) -> List["BasicBlock"]:
        return self._incoming_basic_blocks.get(key, [])

    def outgoing_basic_blocks(self, key: int) -> List["BasicBlock"]:
        return self._outgoing_basic_blocks.get(key, [])

    @property
    def incoming_basic_blocks_as_dict(self) -> Dict[int, List["BasicBlock"]]:
        return self._incoming_basic_blocks

    @property
    def outgoing_basic_blocks_as_dict(self) -> Dict[int, List["BasicBlock"]]:
        return self._outgoing_basic_blocks

    @property
    def all_incoming_basic_blocks(self) -> List["BasicBlock"]:
        bbs_ = self._incoming_basic_blocks.values()
        bbs = [bb for sublist in bbs_ for bb in sublist]
        return list(set(bbs))

    @property
    def all_outgoing_basic_blocks(self) -> List["BasicBlock"]:
        bbs_ = self._outgoing_basic_blocks.values()
        bbs = [bb for sublist in bbs_ for bb in sublist]
        return list(set(bbs))

    def add_incoming_basic_block(self, father: "BasicBlock", key: int) -> None:
        if not key in self._incoming_basic_blocks:
            self._incoming_basic_blocks[key] = []
        if father not in self._incoming_basic_blocks[key]:
            self._incoming_basic_blocks[key].append(father)

    def add_outgoing_basic_block(self, son: "BasicBlock", key: int) -> None:
        if not key in self._outgoing_basic_blocks:
            self._outgoing_basic_blocks[key] = []
        if son not in self._outgoing_basic_blocks[key]:
            self._outgoing_basic_blocks[key].append(son)

    def ends_with_jumpi(self) -> bool:
        return self.end.name == "JUMPI"

    def ends_with_jump_or_jumpi(self) -> bool:
        return self.end.name in ("JUMP", "JUMPI")
