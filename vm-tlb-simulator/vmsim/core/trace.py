"""
Trace format for address translation.

Each translation produces a list of TraceStep records that
the visualizer (Person 6) renders step-by-step. Every module
that participates in translation (segmentation, paging, TLB,
fault handler) appends a step to the trace.

This is the contract between modules and the visualizer.
DON'T change field names without telling Person 6.

Owner: Person 6 (defined here so modules can use it from day 1).
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceStep:
    """One step in an address translation.

    stage: short identifier of which subsystem produced this step.
      Examples: "segmentation", "tlb", "page_table_l3", "page_table_l2",
                "page_table_l1", "page_table_l0", "page_fault",
                "swap_in", "physical_access".

    description: human-readable explanation shown to the user.

    input_value: integer input to this step (typically an address).
    output_value: integer output (typically an address or frame).

    hit: True for hit/success, False for miss/fault, None if N/A.

    metadata: anything extra a module wants to attach (e.g. PTE flags,
              level number, segment name, replacement victim).
    """
    stage: str
    description: str
    input_value: int | None = None
    output_value: int | None = None
    hit: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Convenience: a "trace" is just a list of steps.
Trace = list[TraceStep]
