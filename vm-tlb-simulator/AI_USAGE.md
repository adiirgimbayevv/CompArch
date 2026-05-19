# AI usage log

The course requires us to document how we used AI agents (Claude Code,
Codex, GitHub Copilot, etc.) — see Stage 3 of the assignment.

Each team member fills in their own section below. Be specific: paste
actual prompts you wrote and a short note on what worked, what didn't,
and where you had to push back / debug the AI's output.

---

## Person 1 — Segmentation, core types, CLI

**Tool:** Claude Code

**Prompts:**

1. _"Reference module — provided as project skeleton. Used Claude
   to review the segment-bounds checking logic and to add the
   `make_default_segment_table()` helper."_

**Tricky moments:**

- Decided to put the selector in the high 16 bits of the 64-bit logical
  address to leave room for a full 48-bit offset (matches our paging layer).

---

## Person 2 — Single-level page table

**Tool:**

**Prompts:**

1.

**Tricky moments:**

---

## Kim Viktoriya — Multi-level page table

**Tool:**
Claude

**Prompts:**

1. Implement map() in vmsim/paging/multi_level.py. Walk the tree from self._root, create empty dicts at missing levels, and store the PTE at the leaf. Increment _intermediate_tables_allocated when creating a new dict.
2. Implement lookup() in vmsim/paging/multi_level.py. Return None if any intermediate level is missing, otherwise return the PTE at the leaf.
3. Implement translate() in vmsim/paging/multi_level.py. Append a TraceStep per level walked. Raise PageFault if a level is missing or the PTE is invalid. Use vmsim/segmentation/segments.py as a reference for the trace pattern.

**Tricky moments:**

1. Understanding that map() walks indices[:-1] (creating intermediate dicts) and uses indices[-1] to place the PTE at the leaf.
2. Setting pte.accessed = True is important, page replacement policies depend on this bit.

## Person 4 — TLB + replacement policies

**Tool:**

**Prompts:**

1.

**Tricky moments:**

---

## Person 5 — Page faults + swap

**Tool:**

**Prompts:**

1.

**Tricky moments:**

---

## Person 6 — Visualization, workloads, plots

**Tool:**

**Prompts:**

1.

**Tricky moments:**
