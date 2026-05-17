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

from vmsim.segmentation import (
    SegmentationFault,
    make_default_segment_table,
    SegmentTable,
)
from vmsim.visualization import print_trace


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
    """Full pipeline. Wires together: segmentation -> TLB -> page table -> fault handler.

    TODO Person 1 (after the team's modules are ready):
      - build SegmentTable + PageTable (single or multi based on --mode)
      - build TLB + PageFaultHandler
      - call segmentation.translate, then TLB.lookup, then page_table.translate,
        catching PageFault to call handler.handle and retry.
    """
    print("TODO Person 1: wire up the full pipeline once Persons 2-5 finish.")
    print("For now, run `python main.py demo-segmentation` to see segmentation.")
    return 1


def cmd_experiments(args: argparse.Namespace) -> int:
    """Run the TLB hit-rate / page-fault experiments and save plots.

    TODO Person 6: implement after the team's pipeline works.
    """
    print("TODO Person 6: run experiments and produce matplotlib plots.")
    return 1


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
        return cmd_experiments(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
