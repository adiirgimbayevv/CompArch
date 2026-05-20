from vmsim.core import (
    PTE,
    PhysicalAddress,
    PhysicalMemory,
    TraceStep,
    Trace,
    Translator,
    PAGE_SHIFT,
    PAGE_MASK,
)


class PageFault(Exception):
    def __init__(self, vpn: int, message: str = ""):
        self.vpn = vpn
        super().__init__(message or f"page fault on VPN {vpn:#x}")


class SingleLevelPageTable(Translator):
    def __init__(self, physical_memory: PhysicalMemory) -> None:
        self.memory = physical_memory
        self._entries: dict[int, PTE] = {}

    def map(self, vpn: int, pte: PTE) -> None:
        self._entries[vpn] = pte

    def unmap(self, vpn: int) -> None:
        self._entries.pop(vpn, None)

    def lookup(self, vpn: int) -> PTE | None:
        return self._entries.get(vpn)

    def translate(self, address: int, trace: Trace) -> int:
        vpn = address >> PAGE_SHIFT
        offset = address & PAGE_MASK
        pte = self._entries.get(vpn)

        if pte is None or not pte.valid:
            trace.append(TraceStep(
                stage="page_table",
                description=f"VPN {vpn:#x} not mapped or invalid",
                input_value=address,
                hit=False,
                metadata={"vpn": vpn, "offset": offset},
            ))
            raise PageFault(vpn)

        pte.referenced = True
        physical_address = PhysicalAddress.from_frame(pte.frame_number, offset).value

        trace.append(TraceStep(
            stage="page_table",
            description=f"Translated VPN {vpn:#x} -> Frame {pte.frame_number:#x}",
            input_value=address,
            output_value=physical_address,
            hit=True,
            metadata={"vpn": vpn, "frame": pte.frame_number, "offset": offset},
        ))
        return physical_address

    def __len__(self) -> int:
        return len(self._entries)
