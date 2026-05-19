from vmsim.core import TraceStep


def format_step(step: TraceStep) -> str:
    """Formats a single TraceStep for console output."""
    hit_str = {True: "HIT", False: "MISS", None: "---"}.get(step.hit, str(step.hit))
    in_str  = f"{step.input_value:#x}"  if step.input_value  is not None else "?"
    out_str = f" -> {step.output_value:#x}" if step.output_value is not None else ""
    return f"  [{step.stage:<20}] {hit_str:<4}  in={in_str}{out_str}  | {step.description}"


def render_trace(history: list) -> str:
    """Converts the simulation history into a readable string."""
    return "\n".join([format_step(s) for s in history])


def print_trace(history: list):
    """Prints the formatted trace to the terminal."""
    if history:
        print(render_trace(history))
