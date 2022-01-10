import logging
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from evm_cfg_builder.cfg.cfg import CFG
    from evm_cfg_builder.cfg.basic_block import BasicBlock

logger = logging.getLogger("evm-cfg-builder")


# pylint: disable=too-many-instance-attributes
class Function:
    DISPATCHER_ID = -2
    FALLBACK_ID = -1

    def __init__(self, hash_id: int, start_addr: int, entry_basic_block: "BasicBlock", cfg: "CFG"):
        self._hash_id: int = hash_id
        self._start_addr: int = start_addr
        self._entry: "BasicBlock" = entry_basic_block
        if hash_id == self.FALLBACK_ID:
            self.name = "_fallback"
        elif hash_id == Function.DISPATCHER_ID:
            self.name = "_dispatcher"
        else:
            self._name = hex(hash_id)
        self._basic_blocks: List["BasicBlock"] = []
        self._attributes: List[str] = []
        self._cfg: "CFG" = cfg

    def __repr__(self) -> str:
        return f"<cfg Function@{hex(self.start_addr)}>"

    @property
    def start_addr(self) -> int:
        return self._start_addr

    @property
    def hash_id(self) -> int:
        return self._hash_id

    @property
    def key(self) -> int:
        return self.hash_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n: str) -> None:
        self._name = n

    @property
    def basic_blocks(self) -> List["BasicBlock"]:
        """
        Returns
            list(BasicBlock)
        """
        return self._basic_blocks

    @basic_blocks.setter
    def basic_blocks(self, bbs: List["BasicBlock"]) -> None:
        self._basic_blocks = bbs

    @property
    def entry(self) -> "BasicBlock":
        return self._entry

    @property
    def attributes(self) -> List[str]:
        """
        Returns
            list(str)
        """
        return self._attributes

    def add_attributes(self, attr: str) -> None:
        if not attr in self.attributes:
            self._attributes.append(attr)

    def check_payable(self) -> None:
        entry = self.entry
        if any(ins.name == "CALLVALUE" for ins in entry.instructions):
            return
        self.add_attributes("payable")

    def check_view(self) -> None:
        changing_state_ops = [
            "CREATE",
            "CREATE2",
            "CALL",
            "CALLCODE",
            "DELEGATECALL",
            "SELFDESTRUCT",
            "SSTORE",
        ]

        for bb in self.basic_blocks:
            if any(ins.name in changing_state_ops for ins in bb.instructions):
                return

        self.add_attributes("view")

    def check_pure(self) -> None:
        state_ops = [
            "CREATE",
            "CREATE2",
            "CALL",
            "CALLCODE",
            "DELEGATECALL",
            "SELFDESTRUCT",
            "SSTORE",
            "ADDRESS",
            "BALANCE",
            "ORIGIN",
            "CALLER",
            "CALLVALUE",
            "CALLDATALOAD",
            "CALLDATASIZE",
            "CALLDATACOPY",
            "CODESIZE",
            "CODECOPY",
            "EXTCODESIZE",
            "EXTCODEHASH",
            "EXTCODECOPY",
            "RETURNDATASIZE",
            "RETURNDATACOPY",
            "BLOCKHASH",
            "COINBASE",
            "TIMESTAMP",
            "NUMBER",
            "DIFFICULTY",
            "GASLIMIT",
            "LOG0",
            "LOG1",
            "LOG2",
            "LOG3",
            "LOG4",
            "CALL",
            "CALLCODE",
            "DELEGATECALL",
            "STATICCALL",
            "SELFDESTRUCT",
            "SSTORE",
            "SLOAD",
        ]

        for bb in self.basic_blocks:
            if any(ins.name in state_ops for ins in bb.instructions):
                return

        self.add_attributes("pure")

    def __str__(self) -> str:
        attrs = ""
        if self.attributes:
            attrs = ", " + ",".join(self.attributes)
        return f"{self.name}, {len(self.basic_blocks)} #bbs {attrs}"

    def output_to_dot(self, base_filename: str) -> None:

        if self.key == Function.DISPATCHER_ID:
            self.output_dispatcher_to_dot(base_filename)
            return

        with open(f"{base_filename}{self.name}.dot", "w", encoding="utf-8") as f:
            f.write("digraph{\n")
            for basic_block in self.basic_blocks:
                instructions_ = [f"{hex(ins.pc)}:{str(ins)}" for ins in basic_block.instructions]
                instructions = "\n".join(instructions_)

                f.write(f'{basic_block.start.pc}[label="{instructions}", shape=box]\n')

                for son in basic_block.outgoing_basic_blocks(self.key):
                    f.write(f"{basic_block.start.pc} -> {son.start.pc}\n")

                if not basic_block.outgoing_basic_blocks(self.key):
                    if basic_block.ends_with_jump_or_jumpi():
                        logger.error(
                            f"Missing branches {self.name} ({self.key}):{hex(basic_block.end.pc)}"
                        )

            f.write("\n}")

    def output_dispatcher_to_dot(self, base_filename: str) -> None:

        with open(f"{base_filename}{self.name}.dot", "w", encoding="utf-8") as f:
            f.write("digraph{\n")
            for basic_block in self.basic_blocks:
                instructions_ = [f"{hex(ins.pc)}:{str(ins)}" for ins in basic_block.instructions]
                instructions = "\n".join(instructions_)

                f.write(f'{basic_block.start.pc}[label="{instructions}"]\n')

                for son in basic_block.outgoing_basic_blocks(self.key):
                    f.write(f"{basic_block.start.pc} -> {son.start.pc}\n")

                if not basic_block.outgoing_basic_blocks(self.key):
                    if basic_block.ends_with_jump_or_jumpi():
                        logger.error(f"Missing branches {self.name}:{hex(basic_block.end.pc)}")
            for function in self._cfg.functions:
                if function != self:
                    f.write(f'{function.start_addr}[label="Call {function.name}"]\n')

            f.write("\n}")
