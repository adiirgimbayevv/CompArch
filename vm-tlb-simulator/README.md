# Virtual Memory and TLB Simulator

A simulator for virtual memory address translation. Implements segmentation,
single-level and multi-level (x86-64 style) page tables, a TLB with
configurable replacement policies, page faults, and swap. Includes a
step-by-step CLI visualizer and matplotlib plots of TLB hit rates.

## Quick start (web interface)

​```
pip install -r requirements.txt
python app.py
​```

Then open **http://localhost:5000** in your browser. The page lets you
translate any virtual address, watch each stage of the pipeline animate
step by step, and inspect the live state of the TLB, page table, and
physical memory.

## Quick start

```bash
pip install -r requirements.txt

# Run the segmentation demo (works out of the box)
python main.py demo-segmentation

# Translate a single virtual address through the full pipeline
python main.py translate --mode multi-level --address 0x12345

# Run experiments and generate plots
python main.py experiments
```

## Architecture

```
                    logical address (64-bit)
                            │
                            ▼
                     [ Segmentation ]   ← Tashmetov Abay (1)
                            │
                            ▼ linear (virtual) address
                            │
                       [ TLB lookup ]    ← Irgimbaev Adi (4)
                            │
                  hit ◄─────┴─────► miss
                   │                 │
                   │                 ▼
                   │       [ Page Table walk ]   ← Koshkinbai Nurbek (2)
                   │                            ← Kim Viktoriya (3)
                   │                 │
                   │       valid ◄───┴───► invalid (PageFault)
                   │         │                 │
                   │         │                 ▼
                   │         │      [ Page Fault Handler + Swap ]   ← Akzhigit Dias (5)
                   │         │                 │
                   ▼         ▼                 ▼
                  physical address
                            │
                            ▼
                  [ Visualization / plots ]    ← Mussakhan Almat (6)
```

## Module map (who owns what)

| Module                            | Owner                 | Status  |
|-----------------------------------|-----------------------|---------|
| `vmsim/core/*`                    | Tashmetov Abay (1)    | ✅ done  |
| `vmsim/segmentation/segments.py`  | Tashmetov Abay (1)    | ✅ done  |
| `main.py` (final pipeline wiring) | Tashmetov Abay (1)    | ✅ done  |
| `vmsim/paging/single_level.py`    | Koshkinbai Nurbek (2) | ✅ done  |
| `vmsim/paging/multi_level.py`     | Kim Viktoriya (3)     | ✅ done  |
| `vmsim/policies/*`                | Irgimbaev Adi (4)     | ✅ done  |
| `vmsim/tlb/tlb.py`                | Irgimbaev Adi (4)     | ✅ done  |
| `vmsim/faults/handler.py`         | Akzhigit Dias (5)     | ✅ done  |
| `vmsim/faults/swap.py`            | Akzhigit Dias (5)     | ✅ done  |
| `vmsim/visualization/tracer.py`   | Mussakhan Almat (6)   | ✅ done  |
| `vmsim/visualization/workload.py` | Mussakhan Almat (6)   | ✅ done  |
| `vmsim/visualization/plots.py`    | Mussakhan Almat (6)   | ✅ done  |

For per-person notes on how AI assistance was used, see `AI_USAGE.md`.
## How translation works

A virtual address goes through up to three stages:

1. **Segmentation** turns a logical address (selector + offset) into a linear
   address. We use 16-bit selectors and 48-bit offsets. Segments check bounds.
2. **TLB lookup** caches recent virtual-page → physical-frame mappings. On a
   hit, the page-table walk is skipped entirely.
3. **Page table walk** translates the linear address by walking either a
   flat single-level page table or a 4-level page table. On an invalid PTE,
   a `PageFault` is raised and handed to the **page-fault handler**, which
   allocates a frame (evicting + swapping out an existing one if needed),
   swaps in the page if applicable, and updates the PTE.

Every step appends a `TraceStep` to a shared trace list, which the
visualizer renders.

## Project layout

```
vm-tlb-simulator/
├── README.md
├── AI_USAGE.md
├── requirements.txt
├── main.py              ← Tashmetov Abay (CLI entry point)
├── app.py               ← Flask web server
├── static/              ← CSS and JS for the web
├── templates/           ← HTML pages for the web
└── vmsim/
    ├── core/            ← Tashmetov Abay (shared types)
    ├── segmentation/    ← Tashmetov Abay
    ├── paging/          ← Koshkinbai Nurbek and Kim Viktoriya
    ├── tlb/             ← Irgimbaev Adi
    ├── policies/        ← Irgimbaev Adi (shared FIFO/LRU/Clock)
    ├── faults/          ← Akzhigit Dias
    └── visualization/   ← Mussakhan Almat  
```

## Conventions

- **Type hints everywhere.** They double as documentation and catch bugs.
- **Docstring at the top of every file** stating who owns it.
- **TraceStep on every translation step.** The visualizer relies on this.
- **Use `vmsim.core` for shared types**, never re-define address/PTE locally.
- **Don't hardcode** `PAGE_SIZE`, `LEVELS`, etc — import them.

