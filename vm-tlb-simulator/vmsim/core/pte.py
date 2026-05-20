"""
Page Table Entry (PTE).

Used by single-level and multi-level page tables, and by the
page-fault handler / replacement policies.

Owner: Person 2 (shared foundation).
"""
from dataclasses import dataclass, field


@dataclass(init=False)
class PTE:
    """Page Table Entry for one virtual page.

    The project spec uses ``referenced`` for the usage bit. Existing
    code in the repository already used ``accessed``. This class keeps
    both names synchronized.
    """

    valid: bool = field(default=False)
    frame_number: int = field(default=0)
    writable: bool = field(default=True)
    user: bool = field(default=True)
    dirty: bool = field(default=False)
    referenced: bool = field(default=False)

    def __init__(
        self,
        valid: bool = False,
        frame_number: int = 0,
        writable: bool = True,
        user: bool = True,
        dirty: bool = False,
        referenced: bool | None = None,
        accessed: bool | None = None,
    ) -> None:
        if frame_number < 0:
            raise ValueError("frame_number must be non-negative")

        if referenced is None and accessed is None:
            referenced = False
        elif referenced is None:
            referenced = accessed
        elif accessed is not None and accessed != referenced:
            raise ValueError("referenced and accessed must match when both are set")

        self.valid = valid
        self.frame_number = frame_number
        self.writable = writable
        self.user = user
        self.dirty = dirty
        self.referenced = bool(referenced)

    @property
    def accessed(self) -> bool:
        return self.referenced

    @accessed.setter
    def accessed(self, value: bool) -> None:
        self.referenced = bool(value)

    def __repr__(self) -> str:
        if not self.valid:
            return "PTE(invalid)"
        flags = []
        if self.writable:
            flags.append("W")
        if self.user:
            flags.append("U")
        if self.referenced:
            flags.append("A")
        if self.dirty:
            flags.append("D")
        return f"PTE(frame={self.frame_number}, {''.join(flags)})"
