# Virtual Memory and TLB Simulator

A simulator for virtual memory address translation. Implements segmentation,
single-level and multi-level (x86-64 style) page tables, a TLB with
configurable replacement policies, page faults, and swap. Includes a
step-by-step CLI visualizer and matplotlib plots of TLB hit rates.

## Quick start

```bash
pip install -r requirements.txt

# Run the segmentation demo (works out of the box)
python main.py demo-segmentation

# Run tests
pytest -v
```

Once Persons 2–6 finish their modules:

```bash
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
                     [ Segmentation ]   ← Person 1
                            │
                            ▼ linear (virtual) address
                            │
                       [ TLB lookup ]    ← Person 4
                            │
                  hit ◄─────┴─────► miss
                   │                 │
                   │                 ▼
                   │       [ Page Table walk ]   ← Person 2 (single-level)
                   │                            ← Person 3 (multi-level)
                   │                 │
                   │       valid ◄───┴───► invalid (PageFault)
                   │         │                 │
                   │         │                 ▼
                   │         │      [ Page Fault Handler + Swap ]   ← Person 5
                   │         │                 │
                   ▼         ▼                 ▼
                  physical address
                            │
                            ▼
                  [ Visualization / plots ]    ← Person 6
```

## Module map (who owns what)

| Module                            | Owner    | Status         |
|-----------------------------------|----------|----------------|
| `vmsim/core/*`                    | Person 1 | ✅ done (foundation) |
| `vmsim/segmentation/segments.py`  | Person 1 | ✅ done (reference module) |
| `main.py` (final pipeline wiring) | Person 1 | ⏳ TODO         |
| `vmsim/paging/single_level.py`    | Person 2 | ⏳ TODO         |
| `vmsim/paging/multi_level.py`     | Person 3 | ⏳ TODO         |
| `vmsim/policies/*`                | Person 4 | ⏳ TODO         |
| `vmsim/tlb/tlb.py`                | Person 4 | ⏳ TODO         |
| `vmsim/faults/handler.py`         | Person 5 | ⏳ TODO         |
| `vmsim/faults/swap.py`            | Person 5 | ⏳ TODO         |
| `vmsim/visualization/tracer.py`   | Person 6 | 🟡 minimal version provided |
| `vmsim/visualization/workload.py` | Person 6 | ⏳ TODO         |
| `vmsim/visualization/plots.py`    | Person 6 | ⏳ TODO         |

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
├── AI_USAGE.md          ← each person logs their AI prompts here
├── requirements.txt
├── main.py              ← CLI entry point
├── vmsim/
│   ├── core/            ← shared types (address, PTE, frame, trace, interfaces)
│   ├── segmentation/    ← Person 1
│   ├── paging/          ← Persons 2 and 3
│   ├── tlb/             ← Person 4
│   ├── policies/        ← Person 4 (shared FIFO/LRU/Clock)
│   ├── faults/          ← Person 5
│   └── visualization/   ← Person 6
└── tests/
```

## Conventions

- **Type hints everywhere.** They double as documentation and catch bugs.
- **Docstring at the top of every file** stating who owns it.
- **TraceStep on every translation step.** The visualizer relies on this.
- **Test your own module.** Each person writes `tests/test_<your_module>.py`.
  See `tests/test_segmentation.py` for the pattern.
- **Use `vmsim.core` for shared types**, never re-define address/PTE locally.
- **Don't hardcode** `PAGE_SIZE`, `LEVELS`, etc — import them.

## Running tests

```bash
pytest -v                              # all tests
pytest tests/test_segmentation.py -v   # one module
pytest -v -k "page_table"              # tests matching a name
```

CI runs tests automatically on every push (see `.github/workflows/`).
