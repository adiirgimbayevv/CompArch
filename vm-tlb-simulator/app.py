"""
Web interface for the Virtual Memory and TLB Simulator.

Run with:
    pip install flask
    python app.py

Then open http://localhost:5000 in your browser.
"""
from flask import Flask, render_template, request, jsonify
from dataclasses import asdict

from vmsim.segmentation import (
    SegmentationFault,
    make_default_segment_table,
    SegmentTable,
)
from vmsim.core import PTE, PhysicalMemory, PAGE_SHIFT, PAGE_MASK
from vmsim.paging.multi_level import MultiLevelPageTable
from vmsim.paging.single_level import SingleLevelPageTable, PageFault
from vmsim.tlb import TLB
from vmsim.faults import PageFaultHandler, SwapArea


app = Flask(__name__)


# Global simulator state — preserved across requests so TLB and page table
# remember previous translations (gives nice cache hit demos).
class SimulatorState:
    def __init__(self):
        self.reset(mode="multi-level", tlb_policy="lru", tlb_capacity=4, frames=8)

    def reset(self, mode: str, tlb_policy: str, tlb_capacity: int, frames: int):
        self.mode = mode
        self.tlb_policy = tlb_policy
        self.tlb_capacity = tlb_capacity
        self.frames = frames

        self.seg_table = make_default_segment_table()
        self.memory = PhysicalMemory(num_frames=frames)
        self.swap = SwapArea()

        if mode == "single-level":
            self.page_table = SingleLevelPageTable(self.memory)
        else:
            self.page_table = MultiLevelPageTable(self.memory)

        self.tlb = TLB(capacity=tlb_capacity, policy_name=tlb_policy)
        self.fault_handler = PageFaultHandler(
            self.memory, self.swap, policy_name=tlb_policy
        )
        self.fault_handler.attach_page_table(self.page_table)

        self.history = []  # list of past translations for display


state = SimulatorState()


def step_to_dict(step) -> dict:
    """Convert TraceStep dataclass to JSON-friendly dict."""
    return {
        "stage": step.stage,
        "description": step.description,
        "input_value": f"{step.input_value:#x}" if step.input_value is not None else None,
        "output_value": f"{step.output_value:#x}" if step.output_value is not None else None,
        "hit": step.hit,
        "metadata": {k: (f"{v:#x}" if isinstance(v, int) and v > 1000 else v)
                     for k, v in step.metadata.items()},
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """Run one address through the full translation pipeline."""
    data = request.json or {}
    try:
        address = int(data.get("address", "0x0"), 0)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid address format"}), 400

    trace = []
    result = {
        "input_address": f"{address:#x}",
        "steps": [],
        "final_physical": None,
        "error": None,
        "tlb_hits": state.tlb.hits,
        "tlb_misses": state.tlb.misses,
        "page_faults_before": state.fault_handler.faults,
    }

    try:
        # Stage 1: Segmentation
        linear = state.seg_table.translate(address, trace)

        # Stage 2/3: TLB + Page Table
        vpn = linear >> PAGE_SHIFT
        offset = linear & PAGE_MASK

        cached_frame = state.tlb.lookup(vpn, trace)
        if cached_frame is not None:
            physical = (cached_frame << PAGE_SHIFT) | offset
        else:
            # TLB miss — walk page table
            try:
                physical = state.page_table.translate(linear, trace)
            except PageFault:
                # Stage 4: Page fault handling
                state.fault_handler.handle(vpn, trace)
                physical = state.page_table.translate(linear, trace)

            # Insert into TLB for next time
            frame_number = physical >> PAGE_SHIFT
            state.tlb.insert(vpn, frame_number)

        result["final_physical"] = f"{physical:#x}"

    except SegmentationFault as e:
        result["error"] = f"Segmentation fault: {e}"
    except Exception as e:
        result["error"] = f"Error: {type(e).__name__}: {e}"

    result["steps"] = [step_to_dict(s) for s in trace]
    result["tlb_hits"] = state.tlb.hits
    result["tlb_misses"] = state.tlb.misses
    result["tlb_hit_rate"] = round(state.tlb.hit_rate * 100, 1)
    result["page_faults"] = state.fault_handler.faults
    result["page_faults_now"] = state.fault_handler.faults - result["page_faults_before"]
    result["memory_used"] = state.memory.num_allocated
    result["memory_total"] = state.memory.num_frames
    result["swap_size"] = len(state.swap)

    state.history.append({
        "address": f"{address:#x}",
        "result": result["final_physical"] or "FAULT",
        "tlb_hit": any(s.stage == "tlb" and s.hit for s in trace),
    })
    if len(state.history) > 20:
        state.history = state.history[-20:]

    result["history"] = state.history
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset the simulator with new configuration."""
    data = request.json or {}
    mode = data.get("mode", "multi-level")
    tlb_policy = data.get("tlb_policy", "lru")
    tlb_capacity = int(data.get("tlb_capacity", 4))
    frames = int(data.get("frames", 8))

    state.reset(mode, tlb_policy, tlb_capacity, frames)
    return jsonify({"status": "ok"})


@app.route("/api/config", methods=["GET"])
def api_config():
    """Return current simulator configuration and stats."""
    return jsonify({
        "mode": state.mode,
        "tlb_policy": state.tlb_policy,
        "tlb_capacity": state.tlb_capacity,
        "frames": state.frames,
        "tlb_hits": state.tlb.hits,
        "tlb_misses": state.tlb.misses,
        "tlb_hit_rate": round(state.tlb.hit_rate * 100, 1),
        "page_faults": state.fault_handler.faults,
        "memory_used": state.memory.num_allocated,
        "memory_total": state.memory.num_frames,
        "swap_size": len(state.swap),
        "history": state.history,
    })


@app.route("/api/segments", methods=["GET"])
def api_segments():
    """Return the segment table for display."""
    segments = []
    for selector, seg in state.seg_table._segments.items():
        segments.append({
            "selector": f"{selector:#x}",
            "name": seg.name,
            "base": f"{seg.base:#x}",
            "limit": f"{seg.limit:#x}",
            "perms": ("r" if seg.readable else "-") +
                     ("w" if seg.writable else "-") +
                     ("x" if seg.executable else "-"),
        })
    return jsonify({"segments": segments})


if __name__ == "__main__":
    print("=" * 60)
    print("Virtual Memory Simulator — Web Interface")
    print("=" * 60)
    print("Open in your browser: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
