"""
Owner: Person 6 (Visualization)
Description: Formats and renders simulation traces.
"""
from vmsim.core import TraceStep

def format_step(step_data: TraceStep) -> str:
    """Formats a single simulation step for the console output."""
    # Обращаемся к атрибутам объекта (address, hit), а не к ключам словаря
    addr = hex(step_data.address) if isinstance(step_data.address, int) else str(step_data.address)
    status = "Hit" if step_data.hit else "Miss"
    return f"Access: {addr} | {status}"

def render_trace(history: list[TraceStep]) -> str:
    """Converts the simulation history into a readable string."""
    return "\n".join([format_step(s) for s in history])

def print_trace(history: list[TraceStep]):
    """Prints the formatted trace to the terminal."""
    print(render_trace(history))
