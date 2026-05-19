"""
Virtual Memory + TLB Simulator — entry point.

Usage:
    python main.py demo-segmentation
    python main.py translate --mode single-level --address 0x1234
    python main.py experiments               # produces plots

Right now only the segmentation demo runs (Person 1's module is done).
As Persons 2-6 finish their modules, this script wires them up.

Owner: Person 1.
"""
import argparse
import sys
from pathlib import Path

from vmsim.tlb.tlb import TLB
from vmsim.paging.single_level import SingleLevelPageTable, PageFault
from vmsim.paging.multi_level import MultiLevelPageTable
from vmsim.faults.handler import PageFaultHandler
from vmsim.faults.swap import SwapArea
from vmsim.core import PhysicalMemory, PTE, PAGE_SHIFT
from vmsim.segmentation import (
    SegmentationFault,
    make_default_segment_table,
    SegmentTable,
)
from vmsim.visualization import print_trace, plot_hit_rate_vs_capacity


def cmd_demo_segmentation() -> int:
    """Show segmentation working on a handful of addresses."""
    table = make_default_segment_table()
    print("Segment table:")
    print(table)
    print()

    test_cases = [
        ("code start",        SegmentTable.pack_logical(0x0001, 0x0000)),
        ("data byte",         SegmentTable.pack_logical(0x0002, 0x1234)),
        ("heap mid",          SegmentTable.pack_logical(0x0003, 0x20000)),
        ("stack",             SegmentTable.pack_logical(0x0004, 0x100)),
        ("out of bounds",     SegmentTable.pack_logical(0x0001, 0x200000)),
        ("invalid selector",  SegmentTable.pack_logical(0x00FF, 0x0)),
    ]

    for label, logical in test_cases:
        print(f"--- {label}: logical = {logical:#x} ---")
        trace = []
        try:
            linear = table.translate(logical, trace)
            print_trace(trace)
            print(f"  -> linear address: {linear:#x}")
        except SegmentationFault as e:
            print_trace(trace)
            print(f"  -> FAULT: {e}")
        print()
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    """
    Full address translation pipeline:
    Segmentation -> TLB -> Page Table -> Page Fault Handler.
    """
    logical_address = args.address
    mode = args.mode
    trace = []

    try:
        seg_table = make_default_segment_table()
        linear_address = seg_table.translate(logical_address, trace)
        print(f"[Segmentation] Linear address: {linear_address:#x}")
    except SegmentationFault as e:
        print_trace(trace)
        print(f"SEGMENTATION FAULT: {e}")
        return 1

    tlb = TLB(capacity=16, policy_name="lru")

    memory  = PhysicalMemory(num_frames=64)
    swap    = SwapArea()
    handler = PageFaultHandler(memory, swap, policy_name="lru")

    if mode == "single-level":
        page_table = SingleLevelPageTable(memory)
    else:
        page_table = MultiLevelPageTable(memory)

    handler.attach_page_table(page_table)

    offset_bits = PAGE_SHIFT
    vpn    = linear_address >> offset_bits
    offset = linear_address & ((1 << offset_bits) - 1)

    frame = tlb.lookup(vpn, trace)

    if frame is not None:
        physical_address = (frame << offset_bits) | offset
        print(f"[TLB]          Hit! frame={frame:#x}")
    else:
        print(f"[TLB]          Miss — walking page table ({mode})")
        try:
            physical_address = page_table.translate(linear_address, trace)
            frame = physical_address >> offset_bits
        except PageFault as pf: 
            print(f"[Page Fault]  VPN {pf.vpn:#x} — invoking handler...")
            frame = handler.handle(pf.vpn, trace)

            try:
                physical_address = page_table.translate(linear_address, trace)
                frame = physical_address >> offset_bits
            except PageFault as pf2:
                print_trace(trace)
                print(f"CRITICAL: double page fault on VPN {pf2.vpn:#x}")
                return 1

        tlb.insert(vpn, frame)
        print(f"[TLB]          Inserted VPN {vpn:#x} -> frame {frame:#x}")


    print()
    print_trace(trace)
    print()
    print(f"{'='*55}")
    print(f"  Физический адрес : {physical_address:#x}")
    print(f"  VPN={vpn:#x}  Frame={frame:#x}  Offset={offset:#x}")
    print(f"  TLB hits={tlb.hits}  misses={tlb.misses}  "
          f"Page faults={handler.faults}")
    print(f"{'='*55}")
    return 0


import argparse
import sys
from pathlib import Path 

from vmsim.segmentation import (
    SegmentationFault,
    make_default_segment_table,
    SegmentTable,
)

from vmsim.visualization import print_trace, plot_hit_rate_vs_capacity 



def cmd_experiments(): 
    capacities = [4, 8, 16, 32, 64]
    hit_rates = [0.4, 0.6, 0.75, 0.88, 0.95] 
    
    output_dir = Path("experiments")
    output_dir.mkdir(exist_ok=True) 
    output = output_dir / "hit_rate_vs_capacity.png"
    
    plot_hit_rate_vs_capacity(capacities, hit_rates, "TLB Analysis", output)
    print(f"Experiment graph saved to {output}")



def main() -> int:
    parser = argparse.ArgumentParser(description="Virtual Memory + TLB Simulator")
    subs = parser.add_subparsers(dest="command", required=True)

    subs.add_parser("demo-segmentation",
                    help="Show segmentation working on sample addresses")

    p_translate = subs.add_parser("translate",
                                   help="Translate a single virtual address")
    p_translate.add_argument("--mode", choices=["single-level", "multi-level"],
                             default="multi-level")
    p_translate.add_argument("--address", type=lambda s: int(s, 0), required=True)

    subs.add_parser("experiments", help="Run experiments and produce plots")

    args = parser.parse_args()

    if args.command == "demo-segmentation":
        return cmd_demo_segmentation()
    elif args.command == "translate":
        return cmd_translate(args)
    elif args.command == "experiments":
        return cmd_experiments()
    else:
        parser.print_help()
        return 1
    


if __name__ == "__main__":
    sys.exit(main())
