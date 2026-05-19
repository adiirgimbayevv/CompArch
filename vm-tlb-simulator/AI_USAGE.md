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


## Irgimbayev Adi — TLB + replacement policies
Tool: Codex / Gemini

Prompts:
1.Implement vmsim/policies/fifo.py, lru.py, and clock.py. Create a unified policy interface. Use collections.deque for FIFO. Use collections.OrderedDict for LRU, moving elements to the end on access() and using popitem(last=False) for eviction. For Clock, implement a circular array utilizing reference bits (accessed bit) and a moving hand pointer to give pages a second chance.

2.Implement lookup() in vmsim/tlb/tlb.py. Search for the Frame Number using the Virtual Page Number (VPN). Return the physical frame on a TLB Hit, or None on a TLB Miss. Ensure it appends corresponding TraceStep logs for the visualization module to parse.

3.Implement insert(), flush(), and flush_one() in vmsim/tlb/tlb.py. Handle new mappings. If the TLB cache reaches its capacity limit, trigger the active replacement policy's evict() method first. Implement total cache invalidation via flush() and targeted single-page removal via flush_one(vpn).

4.Write unit tests in tests/test_policies.py and tests/test_tlb.py. Verify strict FIFO ordering, correct LRU eviction recency tracking, Clock's second-chance bit manipulation, and valid mathematical calculation of the overall TLB hit_rate.

Tricky moments:
1.Clock Algorithm State Tracking: Managing the index pointer (hand) correctly so it smoothly loops back to 0 when reaching the end of the circular array without throwing index errors.

2.TraceStep Integration: Ensuring that both TLB hits and misses correctly append explicit step objects, as the visualization pipeline (Person 6) completely breaks if any step is missing or malformed.

3.Synchronization with Page Table: Making sure that when flush_one(vpn) is called during a context switch, the TLB clears the specific entry instantly to avoid stale data corruption.
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
