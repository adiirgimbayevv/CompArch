// ===========================================
// Virtual Memory Simulator — Frontend Logic
// ===========================================

const STAGE_DELAY = 600;  // ms between visual stages

const addressInput = document.getElementById("address-input");
const translateBtn = document.getElementById("translate-btn");
const resetBtn = document.getElementById("reset-btn");
const modeSelect = document.getElementById("mode-select");
const policySelect = document.getElementById("policy-select");
const tlbCapacityInput = document.getElementById("tlb-capacity");
const framesInput = document.getElementById("frames-input");

const stages = {
    segmentation: document.getElementById("stage-segmentation"),
    tlb: document.getElementById("stage-tlb"),
    pagetable: document.getElementById("stage-pagetable"),
    fault: document.getElementById("stage-fault"),
};

const treeViz = document.getElementById("tree-viz");
const ptContent = document.getElementById("pt-content");
const resultCard = document.getElementById("result-card");
const resultValue = document.getElementById("result-value");
const traceLog = document.getElementById("trace-log");
const historyList = document.getElementById("history-list");

// Stat displays
const statHits = document.getElementById("stat-hits");
const statMisses = document.getElementById("stat-misses");
const statRate = document.getElementById("stat-rate");
const statFaults = document.getElementById("stat-faults");
const statMemUsed = document.getElementById("stat-mem-used");
const statMemTotal = document.getElementById("stat-mem-total");
const statSwap = document.getElementById("stat-swap");

// Sleep helper
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function resetVisuals() {
    Object.values(stages).forEach((s) => {
        s.classList.remove("active", "success", "fault");
        s.querySelector(".stage-content").textContent = "Awaiting...";
    });
    // Hide fault stage by default
    stages.fault.style.display = "none";

    resultCard.classList.remove("success", "fault");
    resultValue.textContent = "—";

    // Reset tree
    document.querySelectorAll(".tree-level").forEach((lvl) => {
        const existing = lvl.querySelector(".tree-node");
        if (existing) existing.remove();
        const placeholder = lvl.querySelector(".tree-node-placeholder");
        if (placeholder) placeholder.style.display = "";
    });
    ptContent.textContent = "Awaiting walk...";
}

async function activateStage(stageKey, content, statusClass = "active") {
    const stage = stages[stageKey];
    if (!stage) return;

    stage.style.display = "";  // ensure visible
    stage.classList.remove("active", "success", "fault");

    // Force reflow for animation restart
    void stage.offsetWidth;

    stage.classList.add(statusClass);
    if (content !== undefined) {
        stage.querySelector(".stage-content").innerHTML = content;
    }
    await sleep(STAGE_DELAY);
}

function setTreeNode(level, value, status = "active") {
    const lvl = treeViz.querySelector(`.tree-level[data-level="${level}"]`);
    if (!lvl) return;

    const placeholder = lvl.querySelector(".tree-node-placeholder");
    if (placeholder) placeholder.style.display = "none";

    let node = lvl.querySelector(".tree-node");
    if (!node) {
        node = document.createElement("div");
        node.className = "tree-node";
        lvl.appendChild(node);
    }
    node.textContent = value;
    node.className = `tree-node ${status}`;
}

function addTraceStep(step) {
    const div = document.createElement("div");
    let statusClass = "info";
    if (step.hit === true) statusClass = "hit";
    else if (step.hit === false) statusClass = "miss";

    div.className = `trace-step ${statusClass}`;

    const valueStr = (step.input_value && step.output_value)
        ? ` <span class="trace-values">${step.input_value} → ${step.output_value}</span>`
        : step.input_value
        ? ` <span class="trace-values">in: ${step.input_value}</span>`
        : "";

    div.innerHTML = `
        <span class="trace-stage">[${step.stage}]</span>
        <span class="trace-desc">${escapeHtml(step.description)}</span>
        ${valueStr}
    `;
    traceLog.appendChild(div);
}

function escapeHtml(s) {
    if (!s) return "";
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function clearTrace() {
    traceLog.innerHTML = "";
}

function pulse(elem) {
    elem.classList.remove("pulse");
    void elem.offsetWidth;
    elem.classList.add("pulse");
}

function updateStats(data) {
    const oldRate = parseInt(statRate.textContent, 10) || 0;
    statHits.textContent = data.tlb_hits;
    statMisses.textContent = data.tlb_misses;
    statRate.textContent = data.tlb_hit_rate || 0;
    statFaults.textContent = data.page_faults;
    statMemUsed.textContent = data.memory_used;
    statMemTotal.textContent = data.memory_total;
    statSwap.textContent = data.swap_size;

    if (Math.abs((data.tlb_hit_rate || 0) - oldRate) > 0) {
        pulse(statRate.parentElement.parentElement);
    }
}

function updateHistory(history) {
    if (!history || history.length === 0) {
        historyList.innerHTML = '<div class="history-empty">No translations yet.</div>';
        return;
    }
    historyList.innerHTML = "";
    history.slice().reverse().forEach((h) => {
        const item = document.createElement("div");
        let className = "history-item";
        if (h.result === "FAULT") className += " fault";
        else if (!h.tlb_hit) className += " miss";

        item.className = className;
        item.innerHTML = `
            <span class="history-hit-indicator"></span>
            <span>${h.address}</span>
            <span class="history-arrow">→</span>
            <span>${h.result}</span>
        `;
        historyList.appendChild(item);
    });
}

// ============ Main translate function ============

async function runTranslate() {
    const address = addressInput.value.trim();
    if (!address) return;

    translateBtn.disabled = true;
    resetVisuals();
    clearTrace();

    try {
        const response = await fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address: address }),
        });
        const data = await response.json();

        if (data.error && !data.steps.length) {
            // Network or parse error
            resultCard.classList.add("fault");
            resultValue.textContent = data.error;
            translateBtn.disabled = false;
            return;
        }

        // Animate steps one by one
        await animateSteps(data);

        // Update stats and history at the end
        updateStats(data);
        updateHistory(data.history);
        
    } catch (err) {
        console.error(err);
        resultCard.classList.add("fault");
        resultValue.textContent = "Network error: " + err.message;
    } finally {
        translateBtn.disabled = false;
    }
}


async function animateSteps(data) {
    const steps = data.steps;
    let segmentationDone = false;
    let tlbDone = false;

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        addTraceStep(step);

        if (step.stage === "segmentation") {
            const segName = step.metadata.segment || "?";
            const content = step.hit
                ? `Segment <strong>${segName}</strong>: base + offset → ${step.output_value}`
                : `<span style="color:var(--danger)">FAULT</span>: ${escapeHtml(step.description)}`;
            await activateStage("segmentation", content, step.hit ? "success" : "fault");
            segmentationDone = true;
            if (!step.hit) {
                // Stop pipeline on segmentation fault
                resultCard.classList.add("fault");
                resultValue.textContent = data.error || "Segmentation fault";
                return;
            }
        }

        else if (step.stage === "tlb") {
            const content = step.hit
                ? `<span style="color:var(--success)">HIT</span>: VPN ${step.input_value} → frame ${step.output_value}`
                : `<span style="color:var(--warning)">MISS</span>: VPN ${step.input_value} not in cache, walking page table`;
            await activateStage("tlb", content, step.hit ? "success" : "active");
            tlbDone = true;

            if (step.hit) {
                // TLB hit means we skip the page table walk
                resultCard.classList.add("success");
                resultValue.textContent = data.final_physical;
                stages.pagetable.style.opacity = "0.3";
                return;
            }
        }

        else if (step.stage.startsWith("page_table_l")) {
            const level = parseInt(step.stage.slice("page_table_l".length), 10);
            const idx = step.metadata.index || "?";
            setTreeNode(level, idx, step.hit ? "success" : "fault");
            await sleep(STAGE_DELAY / 2);

            if (level === 0) {
                stages.pagetable.classList.add("active");
            }

            if (!step.hit) {
                // Page fault detected
                ptContent.innerHTML = `<span style="color:var(--danger)">Missing at level ${level}</span> — invoking page fault handler`;
                stages.pagetable.classList.remove("active");
                stages.pagetable.classList.add("fault");
                await sleep(STAGE_DELAY);
            }
        }

        else if (step.stage === "physical_access") {
            stages.pagetable.classList.remove("active");
            stages.pagetable.classList.add("success");
            ptContent.innerHTML = `<span style="color:var(--success)">Walk complete</span> — physical = ${step.output_value}`;
            await sleep(STAGE_DELAY / 2);
        }

        else if (step.stage === "page_fault") {
            stages.fault.style.display = "";
            const content = step.hit === false
                ? `<span style="color:var(--danger)">Page fault triggered</span> for VPN ${step.input_value || ""}`
                : `<span style="color:var(--success)">Resolved</span>: ${escapeHtml(step.description)}`;
            await activateStage("fault", content, step.hit === false ? "fault" : "success");
        }

        else if (step.stage === "swap_out") {
            const content = `Evicting page: VPN ${step.input_value} from frame ${step.output_value}`;
            await activateStage("fault", content, "active");
        }

        else if (step.stage === "swap_in") {
            const content = `Restoring page: VPN ${step.input_value} into frame ${step.output_value}`;
            await activateStage("fault", content, "active");
        }
    }

    // Final result
    if (data.error) {
        resultCard.classList.add("fault");
        resultValue.textContent = data.error;
    } else if (data.final_physical) {
        resultCard.classList.add("success");
        resultValue.textContent = data.final_physical;
    }
}

// ============ Event handlers ============

translateBtn.addEventListener("click", runTranslate);
addressInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runTranslate();
});

document.querySelectorAll(".example-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        addressInput.value = chip.dataset.addr;
        runTranslate();
    });
});

resetBtn.addEventListener("click", async () => {
    const config = {
        mode: modeSelect.value,
        tlb_policy: policySelect.value,
        tlb_capacity: parseInt(tlbCapacityInput.value, 10),
        frames: parseInt(framesInput.value, 10),
    };
    await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
    });
    // Refresh stats
    const resp = await fetch("/api/config");
    const data = await resp.json();
    updateStats(data);
    updateHistory(data.history);
    resetVisuals();
    clearTrace();
});

// Initial load
fetch("/api/config")
    .then((r) => r.json())
    .then((data) => {
        updateStats(data);
        updateHistory(data.history);
        statMemTotal.textContent = data.memory_total;
    });

// Hide fault stage initially
stages.fault.style.display = "none";
