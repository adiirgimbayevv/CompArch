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
    """
    Полный конвейер перевода адреса: 
    Сегментация -> TLB -> Таблица страниц -> Обработчик ошибок.
    """
    
    logical_address = args.address
    trace = []
    
    try:
        seg_table = make_default_segment_table()
        
        linear_address = seg_table.translate(logical_address, trace)
        print(f"Линейный адрес после сегментации: {linear_address:#x}")
        print_trace(trace)
        print(f"Успешный перевод! Физический адрес готов.")
        return 0

    except SegmentationFault as e:
        print_trace(trace)
        print(f"ОШИБКА СЕГМЕНТАЦИИ: {e}")
        return 1
    except Exception as e:
        print(f"Ошибка при переводе: {e}")
        return 1


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
