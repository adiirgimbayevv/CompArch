def format_step(step_data: dict) -> str:
    """Formats a single simulation step for the console output."""
    return f"Access: {step_data.get('address')} | Hit: {step_data.get('hit')}"

def render_trace(history: list) -> str:
    """Converts the simulation history into a readable string."""
    return "\n".join([format_step(s) for s in history])

def print_trace(history: list):
    """Prints the formatted trace to the terminal."""
    print(render_trace(history))