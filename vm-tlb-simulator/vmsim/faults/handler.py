"""
Page fault handler.

When the page tables (single- or multi-level) raise PageFault,
the simulator calls the handler. The handler:

  1. Checks if there's a free frame in physical memory.
     - If yes: allocate it.
     - If no: ask the replacement policy to pick a victim VPN,
       swap-out that VPN (if dirty), free its frame.
  2. If the VPN is in swap: swap it in (record swap_in).
     Otherwise: this is the first touch -> zero-filled new page.
  3. Update the page table (lookup PTE for vpn, set valid=True,
     fill in frame_number, clear accessed/dirty).
  4. Append TraceStep records so the visualizer can show the fault.

Owner: Person 5.
"""
from vmsim.core import (
    PTE,
    PhysicalMemory,
    OutOfMemoryError,
    ReplacementPolicy,
    TraceStep,
    Trace,
)
from vmsim.policies import make_policy
from vmsim.faults.swap import SwapArea


class PageFaultHandler:
    """Resolves page faults: allocates frames, swaps in/out, updates PTEs.

    The page table is passed at handle-time (could be single- or
    multi-level — both have the same lookup/map shape). Person 5 may
    extend this to take a small protocol/interface instead.
    """

    def __init__(
        self,
        memory: PhysicalMemory,
        swap: SwapArea,
        policy_name: str = "lru",
    ) -> None:
        self.memory = memory
        self.swap = swap
        # Replacement policy operates on FRAME NUMBERS.
        self.policy: ReplacementPolicy = make_policy(policy_name, memory.num_frames)
        self.policy_name = policy_name
        # Frame -> VPN mapping so we know which PTE to invalidate on eviction.
        self._frame_to_vpn: dict[int, int] = {}
        # VPN -> page table reference, so we can clear the PTE on eviction.
        # (Person 5: simplest is to store a callable that invalidates the PTE,
        # or pass the page table object directly.)
        self._page_table = None  # set via attach_page_table()

        self.faults = 0
        self.evictions = 0

    def attach_page_table(self, page_table) -> None:
        """The simulator wires up the active page table here so the
        handler can update PTEs on swap-in and invalidate them on eviction.
        Page table must have .lookup(vpn) and .map(vpn, pte) methods."""
        self._page_table = page_table

    def handle(self, vpn: int, trace: Trace) -> int:
        """Resolve a page fault for `vpn`. Returns the allocated frame_number.

        Walks through steps described in the module docstring.
        Append TraceSteps with stage='page_fault' (and 'swap_in'/'swap_out'
        when those happen) for each action.
        """
        if self._page_table is None:
            raise RuntimeError("attach a page table before handling faults")

        self.faults += 1
        trace.append(TraceStep(
            stage="page_fault",
            description=f"page fault on VPN {vpn:#x}",
            input_value=vpn,
            hit=False,
            metadata={"vpn": vpn},
        ))

        try:
            frame = self.memory.allocate_frame(vpn)
        except OutOfMemoryError:
            victim_frame = self.policy.evict()
            victim_vpn = self._frame_to_vpn.pop(victim_frame)
            victim_pte = self._page_table.lookup(victim_vpn)
            if victim_pte is None:
                raise RuntimeError(f"missing PTE for victim VPN {victim_vpn:#x}")

            self.swap.swap_out(victim_vpn, dirty=victim_pte.dirty)
            victim_pte.valid = False
            self.memory.free_frame(victim_frame)
            self.evictions += 1

            trace.append(TraceStep(
                stage="swap_out",
                description=(
                    f"evicted VPN {victim_vpn:#x} from frame {victim_frame:#x}"
                ),
                input_value=victim_vpn,
                output_value=victim_frame,
                hit=None,
                metadata={
                    "vpn": victim_vpn,
                    "frame": victim_frame,
                    "dirty": victim_pte.dirty,
                },
            ))

            frame = self.memory.allocate_frame(vpn)

        if self.swap.contains(vpn):
            metadata = self.swap.swap_in(vpn)
            trace.append(TraceStep(
                stage="swap_in",
                description=f"restored VPN {vpn:#x} into frame {frame:#x}",
                input_value=vpn,
                output_value=frame,
                hit=True,
                metadata={"vpn": vpn, "frame": frame, "swap": metadata or {}},
            ))

        pte = self._page_table.lookup(vpn) or PTE()
        pte.valid = True
        pte.frame_number = frame
        pte.accessed = True
        pte.dirty = False
        self._page_table.map(vpn, pte)

        self._frame_to_vpn[frame] = vpn
        if self.policy.contains(frame):
            self.policy.access(frame)
        else:
            self.policy.insert(frame)

        trace.append(TraceStep(
            stage="page_fault",
            description=f"mapped VPN {vpn:#x} to frame {frame:#x}",
            input_value=vpn,
            output_value=frame,
            hit=True,
            metadata={"vpn": vpn, "frame": frame},
        ))
        return frame
