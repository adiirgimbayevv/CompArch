"""
Step-by-step CLI visualization of address translation.

Person 6 owns this. A minimal working version is provided so the
project runs end-to-end from day 1. Person 6 extends it with:
  - color (ANSI codes — no external deps needed)
  - nicer per-stage formatting (boxes / arrows)
  - summary footer (segment used, TLB hit/miss, page-fault flag)

Owner: Person 6.
"""
from vmsim.core import Trace, TraceStep


# ANSI color helpers (no external dependency).
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"


def _color_for_step(step: TraceStep) -> str:
    if step.hit is True:
        return GREEN
    if step.hit is False:
        return RED
    return CYAN


def format_step(step: TraceStep, use_color: bool = True) -> str:
    """Render one TraceStep as a single line."""
    if use_color:
        color = _color_for_step(step)
        stage = f"{BOLD}{color}[{step.stage:>16}]{RESET}"
    else:
        stage = f"[{step.stage:>16}]"

    parts = [stage, step.description]
    if step.input_value is not None and step.output_value is not None:
        parts.append(f"({step.input_value:#x} -> {step.output_value:#x})")
    elif step.input_value is not None:
        parts.append(f"(in: {step.input_value:#x})")
    return " ".join(parts)


def render_trace(trace: Trace, use_color: bool = True) -> str:
    """Render a full trace as a multi-line string."""
    return "\n".join(format_step(s, use_color) for s in trace)


def print_trace(trace: Trace, use_color: bool = True) -> None:
    """Pretty-print a trace to stdout."""
    print(render_trace(trace, use_color))
    # TODO Person 6: add a summary line:
    #   - was there a TLB hit?
    #   - was there a page fault?
    #   - final physical address
    # Extract this info from the trace steps.
