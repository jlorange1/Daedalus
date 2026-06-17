const state = {
  paused: false,
  selectedAgent: 1,
  activePanel: "studio",
  inspectorClosed: false,
  lastStatus: null,
};

const $ = (selector) => document.querySelector(selector);

function toast(message) {
  const box = $("#toast");
  box.textContent = message;
  box.classList.add("show");
  window.setTimeout(() => box.classList.remove("show"), 4200);
}

function setActivePanel(panelName) {
  state.activePanel = panelName;
  document.querySelectorAll(".nav-item").forEach((button) => {
    const active = button.dataset.panel === panelName;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.body.dataset.panel = panelName;
  const target = {
    studio: ".studio-floor",
    queue: ".board",
    builds: ".schedule",
    github: ".inspector",
    cron: ".schedule",
    settings: ".sidebar",
  }[panelName] || ".studio-floor";
  document.querySelector(target)?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
  toast(`${panelName[0].toUpperCase()}${panelName.slice(1)} panel focused.`);
}

function pill(value, goodText = "ON", badText = "OFF") {
  return value ? goodText : badText;
}

function workCard(item, fallbackTag) {
  const title = item?.title || "No work order";
  const file = item?.file || "Queue empty";
  const kind = item?.kind || fallbackTag;
  const stamp = item?.stamp || "";
  const tone = String(kind).toLowerCase().replaceAll(" ", "-");
  return `<article class="work-card state-${tone}">
    <strong>${escapeHtml(title)}</strong>
    <span>${escapeHtml(file)}</span>
    <div class="card-foot"><span class="tag">${escapeHtml(kind)}</span><em>${escapeHtml(stamp)}</em></div>
  </article>`;
}

function emptyLane(status) {
  const labels = {
    inbox: ["Queue clear", "No queued work orders", "STANDBY"],
    running: ["No active run", "Agents are standing by", "IDLE"],
    failed: ["Review clear", "No failed work orders", "CLEAN"],
    done: ["No completions", "Completed work will appear here", "OPEN"],
  };
  const [title, body, stamp] = labels[status] || ["Empty", "No live data", "WAIT"];
  return `<article class="empty-card">
    <div class="empty-orbit" aria-hidden="true"><i></i><i></i><i></i></div>
    <div>
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(body)}</span>
    </div>
    <em>${escapeHtml(stamp)}</em>
  </article>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderQueue(queue) {
  for (const status of ["inbox", "running", "failed", "done"]) {
    const lane = queue[status];
    const list = $(`#${status}List`);
    const tag = status === "inbox" ? "Queued" : status === "running" ? "Active" : status === "failed" ? "Review" : "Done";
    const items = lane.items.slice().reverse();
    $(`#${status}Count`).textContent = lane.count;
    list.innerHTML = items.length
      ? items.slice(0, 4).map((item) => workCard(item, tag)).join("")
      : emptyLane(status);
  }
  const total = queue.inbox.count + queue.running.count + queue.failed.count;
  $("#queueBadge").textContent = total;
  $("#queueCount").textContent = `${total} work orders`;
  document.documentElement.style.setProperty("--live-work-count", String(total));
}

function renderAgents(agents) {
  const coreTypes = ["neural", "tesseract", "liquid", "reactor", "lattice", "prism", "helix", "singularity", "sentinel", "quantum", "forge", "orbital", "spectrum", "archive"];
  const grid = $("#agentGrid");
  grid.innerHTML = agents.map((agent, index) => `
    <article class="agent-desk role-${index} core-${coreTypes[index] || "neural"} ${index === state.selectedAgent ? "selected" : ""}" data-agent="${index}" data-state="${escapeHtml(agent.status)}" title="${escapeHtml(agent.role)}: ${escapeHtml(agent.task)}">
      <div class="agent-link-field" aria-hidden="true"><span></span><span></span><span></span></div>
      <span class="agent-hitbox ${agent.status === "working" ? "working" : ""}">
        <i></i><i></i><i></i><i></i>
      </span>
      <div class="agent-plate" aria-hidden="true">
        <h3>${escapeHtml(agent.role)}</h3>
        <p>${escapeHtml(agent.name)}</p>
        <span class="model-chip ${agent.configured ? "configured" : "missing"}">${escapeHtml(agent.provider || "openrouter")}</span>
        <span class="agent-taskline">${escapeHtml(agent.task)}</span>
        <div class="meter"><b style="--value: ${agent.progress}%"></b></div>
      </div>
    </article>
  `).join("");
  grid.querySelectorAll(".agent-desk").forEach((card) => {
    card.addEventListener("click", () => {
      state.selectedAgent = Number(card.dataset.agent || 0);
      grid.querySelectorAll(".agent-desk").forEach((item) => item.classList.toggle("selected", item === card));
      renderInspector(state.lastStatus);
    });
  });
  renderInspector(state.lastStatus);
}

function renderInspector(status) {
  if (!status) return;
  const agent = status.agents[state.selectedAgent] || status.agents[0];
  const coreTypes = ["neural", "tesseract", "liquid", "reactor", "lattice", "prism", "helix", "singularity", "sentinel", "quantum", "forge", "orbital", "spectrum", "archive"];
  const coreType = coreTypes[state.selectedAgent] || "neural";
  $("#agentInspector").innerHTML = `
    <div class="agent-hero">
      <span class="agent-medallion neural-core core-${coreType}" aria-hidden="true"><i></i><i></i><i></i></span>
      <div>
        <strong>${escapeHtml(agent.role)}</strong>
        <p><span class="state-dot ${agent.status === "working" ? "good" : "warn"}"></span>${escapeHtml(agent.name)} ${escapeHtml(agent.status)}.</p>
      </div>
    </div>
    <div class="inspector-task">
      <span>Current Task</span>
      <p>${escapeHtml(agent.task)}</p>
    </div>
    <div class="inspector-task">
      <span>Department Focus</span>
      <p>${escapeHtml(agent.focus || "Autonomous studio operations")}</p>
    </div>
    <dl class="mini-stats">
      <div><dt>Progress</dt><dd>${agent.progress}%</dd></div>
      <div><dt>Focus</dt><dd>${escapeHtml((agent.focus || agent.role).split(",")[0])}</dd></div>
      <div><dt>Model</dt><dd>${escapeHtml(agent.model.replace(":free", ""))}</dd></div>
      <div><dt>ETA</dt><dd>${agent.status === "working" ? "1h 35m" : "queued"}</dd></div>
      <div><dt>Commit</dt><dd>${status.git.daedalus.clean ? "ready" : "local"}</dd></div>
      <div><dt>Signal</dt><dd>${agent.progress > 80 ? "green" : "watch"}</dd></div>
    </dl>
    <div class="meter"><b style="--value: ${agent.progress}%"></b></div>
  `;
  const rsps = status.git.rsps;
  $("#diffSummary").textContent = rsps.detail && rsps.detail !== "clean"
    ? rsps.detail
    : "+ ForgeBoard scene assets validated\n+ Worker queue ready for next patch\n+ Review packet will appear after the next run";
  $("#branchState").innerHTML = `<span class="state-chip good">${escapeHtml(rsps.branch || "main")}</span><span>${rsps.clean ? "ready" : "changes waiting"}</span>`;
  renderActivityLog(status, agent);
}

function renderActivityLog(status, selectedAgent) {
  const buildReady = status.readiness.java && status.readiness.git_lfs && status.readiness.rsps_repo;
  const rsps = status.git.rsps;
  const hasTask = selectedAgent.task && selectedAgent.task !== "No live work assigned";
  const entries = [
    {
      tone: selectedAgent.status === "working" ? "good" : "warn",
      label: selectedAgent.status === "working" ? "Work" : "Queue",
      text: hasTask ? `${selectedAgent.name} is on ${selectedAgent.task}` : `${selectedAgent.name} has no live assignment`,
    },
    {
      tone: buildReady ? "good" : "warn",
      label: "Gate",
      text: buildReady ? "Build/test gate is ready" : "Install Java 11 and Git LFS to unlock builds",
    },
    {
      tone: rsps.clean ? "good" : "warn",
      label: "Branch",
      text: `${rsps.branch || "main"} ${rsps.clean ? "is clean" : "has local changes"}`,
    },
  ];
  const signalRows = entries.map((entry) => `
    <p class="log-row ${entry.tone}">
      <span>${escapeHtml(entry.label)}</span>
      <b>${escapeHtml(entry.text)}</b>
    </p>
  `).join("");
  const logRows = (status.logs || []).slice().reverse().slice(0, 3).map((entry) => {
    const tail = String(entry.tail || "").trim().split("\n").filter(Boolean).slice(-1)[0] || "No recent output";
    return `<p class="log-row artifact"><span>${escapeHtml(entry.name)}</span><b>${escapeHtml(tail)}</b></p>`;
  }).join("");
  const runRows = (status.runs || []).slice(0, 3).map((run) => `
    <p class="log-row run-manifest">
      <span>${escapeHtml(run.agent_id || run.mode || "worker")}</span>
      <b>${escapeHtml(run.status || "unknown")} / ${escapeHtml(run.workflow_id || "manual")} / ${escapeHtml(run.workflow_step_id || run.work_order_file || "no step")}</b>
    </p>
  `).join("");
  $("#activityLog").innerHTML = signalRows + runRows + logRows;
}

function setInspectorClosed(closed) {
  state.inspectorClosed = closed;
  $(".inspector")?.classList.toggle("inspector-closed", closed);
  $("#closeInspector").textContent = closed ? "+" : "x";
  $("#closeInspector").setAttribute("aria-expanded", String(!closed));
  if (closed) {
    toast("Telemetry collapsed.");
  }
}

function renderReadiness(status) {
  const ready = status.readiness;
  const buildReady = ready.java && ready.git_lfs && ready.rsps_repo;
  $("#autonomyState").innerHTML = `<span class="switch ${status.env.autonomy ? "on" : ""}"></span>${pill(status.env.autonomy)}`;
  $("#topAutonomyState").innerHTML = `<span class="switch ${status.env.autonomy ? "on" : ""}"></span>${pill(status.env.autonomy)}`;
  $("#agentsOnline").textContent = `${status.agents.length} / ${status.agents.length}`;
  $("#buildStatus").innerHTML = `<span class="state-chip ${buildReady ? "good" : "warn"}">${buildReady ? "ready" : "tools"}</span>`;
  $("#githubState").innerHTML = `<span class="state-chip ${status.git.daedalus.clean ? "good" : "warn"}">${status.git.daedalus.clean ? "main" : "local"}</span>`;
  $("#envState").innerHTML = `<span class="state-chip ${buildReady ? "good" : "warn"}">${buildReady ? "healthy" : "Java/LFS"}</span>`;
  $("#testList").innerHTML = [
    ["Java toolchain", ready.java],
    ["Git LFS", ready.git_lfs],
    ["OpenClaw", ready.openclaw],
    ["Server source", ready.rsps_repo],
  ].map(([label, ok]) => `<p><span class="state-dot ${ok ? "good" : "warn"}"></span>${label}<b>${ok ? "ready" : "needed"}</b></p>`).join("");
}

function renderAgency(status) {
  const agency = status.agency;
  if (!agency) return;
  const primaryWorkflow = agency.workflows?.find((item) => item.id === "feature_delivery_mesh") || agency.workflows?.[0];
  const levelText = primaryWorkflow?.levels
    ?.map((level, index) => `<span><b>L${index + 1}</b>${level.map((step) => escapeHtml(step)).join(" + ")}</span>`)
    .join("") || "<span>No workflow levels loaded</span>";
  $("#agencyLayer").innerHTML = `
    <div class="agency-metrics">
      <div><strong>${agency.department_count}</strong><span>Departments</span></div>
      <div><strong>${agency.workflow_count}</strong><span>Workflows</span></div>
      <div><strong>${primaryWorkflow?.max_parallel || 0}</strong><span>Max Parallel</span></div>
    </div>
    <p class="agency-source">Inspired by ${escapeHtml(agency.source?.name || "agency role libraries")} / ${escapeHtml(agency.source?.license || "open source")}.</p>
    <div class="agency-flow">
      <strong>${escapeHtml(primaryWorkflow?.name || "Workflow Mesh")}</strong>
      ${levelText}
    </div>
  `;
  const runs = status.workflow_runs || [];
  $("#workflowRuns").innerHTML = runs.length
    ? runs.slice(0, 3).map((run) => `
      <article class="workflow-run">
        <strong>${escapeHtml(run.workflow_name || run.workflow_id)}</strong>
        <span>${escapeHtml(run.status)} / ${run.done || 0}/${run.step_count || 0} done / ${run.queued || 0} queued</span>
        ${(run.steps || []).filter((step) => step.artifact).slice(0, 2).map((step) => `
          <span class="artifact-summary">${escapeHtml(step.id)} evidence: ${step.artifact.changed_file_count || 0} files / exit ${escapeHtml(step.artifact.validation?.worker_exit_code ?? "n/a")}</span>
        `).join("")}
        ${(run.steps || []).filter((step) => step.status === "awaiting_review").slice(0, 2).map((step) => `
          <button class="approve-step mini-command" data-run="${escapeHtml(run.run_id)}" data-step="${escapeHtml(step.id)}">Approve ${escapeHtml(step.id)}</button>
        `).join("")}
      </article>
    `).join("")
    : `<article class="workflow-run empty"><strong>No active runs</strong><span>Start a workflow to create a manifest and queue its first steps.</span></article>`;
  document.querySelectorAll(".approve-step").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await post("/api/workflow/approve", { run_id: button.dataset.run, step_id: button.dataset.step });
        toast(`Approved workflow step ${button.dataset.step}.`);
        refresh();
      } catch (error) {
        toast(error.message);
      }
    });
  });
}

function renderIntelligence(status) {
  const intelligence = status.intelligence;
  if (!intelligence) return;
  const scenarios = intelligence.profitability?.scenarios || [];
  const profitBody = scenarios.length
    ? `<div class="profit-strip">${scenarios.map((item) => `
        <article class="profit-card ${item.net >= 0 ? "good" : "warn"}">
          <strong>${escapeHtml(item.id)}</strong>
          <span>${item.players} players / ${item.paying_users} payers</span>
          <b>${item.net >= 0 ? "+" : ""}$${item.net}</b>
        </article>
      `).join("")}</div>`
    : `<article class="profit-card warn unavailable">
        <strong>Live data unavailable</strong>
        <span>${escapeHtml(intelligence.profitability?.missing_reason || "No profitability telemetry source configured.")}</span>
        <b>no estimate</b>
      </article>`;
  $("#profitEngine").innerHTML = `
    ${profitBody}
    <p>${escapeHtml(intelligence.profitability?.ethics_policy?.[0] || "Ethical monetization gates active.")}</p>
  `;
  $("#governanceLayer").innerHTML = `
    <div class="governance-grid">
      <div><strong>${intelligence.source_count}</strong><span>Source Patterns</span></div>
      <div><strong>${intelligence.specs.artifact_type_count}</strong><span>Spec Artifacts</span></div>
      <div><strong>${intelligence.prompts.pattern_count}</strong><span>Prompt Patterns</span></div>
      <div><strong>${intelligence.skills.skill_count}</strong><span>Local Skills</span></div>
    </div>
    <div class="gate-list">
      ${intelligence.specs.approval_gates.slice(0, 6).map((gate) => `<span>${escapeHtml(gate.replaceAll("_", " "))}</span>`).join("")}
    </div>
  `;
}

async function refresh() {
  const response = await fetch("/api/status");
  const status = await response.json();
  state.lastStatus = status;
  renderQueue(status.queue);
  renderAgents(status.agents);
  renderReadiness(status);
  renderAgency(status);
  renderIntelligence(status);
}

async function post(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || "request failed");
  }
  return data;
}

function wireControls() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.classList.contains("active")));
    button.addEventListener("click", () => setActivePanel(button.dataset.panel || "studio"));
  });
  $("#closeInspector").addEventListener("click", () => setInspectorClosed(!state.inspectorClosed));
  $("#enqueueOpen").addEventListener("click", () => $("#enqueueDialog").showModal());
  $("#enqueueSubmit").addEventListener("click", async (event) => {
    event.preventDefault();
    try {
      await post("/api/enqueue", {
        title: $("#workTitle").value,
        body: $("#workBody").value,
      });
      $("#enqueueDialog").close();
      toast("Work order added to the studio board.");
      refresh();
    } catch (error) {
      toast(error.message);
    }
  });
  $("#runDuo").addEventListener("click", async () => {
    try {
      const result = await post("/api/action", { action: "run-duo" });
      toast(`OpenClaw duo started. PID ${result.pid}.`);
    } catch (error) {
      toast(error.message);
    }
  });
  $("#runBuild").addEventListener("click", () => {
    const ready = state.lastStatus?.readiness;
    const gateReady = ready?.java && ready?.git_lfs && ready?.rsps_repo;
    toast(gateReady ? "Build/Test gate is ready. Queue a work order or run the coding duo to execute guarded work." : "Build/Test is blocked until Java, Git LFS, and the server source are ready.");
  });
  $("#pushBranch").addEventListener("click", () => {
    const clean = state.lastStatus?.git?.daedalus?.clean;
    toast(clean ? "GitHub is clean. New code is pushed after successful reviewed worker runs." : "Local changes detected. Review and commit before pushing.");
  });
  $("#cronTick").addEventListener("click", async () => {
    try {
      const result = await post("/api/action", { action: "cron-tick" });
      toast(`Cron tick started. PID ${result.pid}.`);
    } catch (error) {
      toast(error.message);
    }
  });
  $("#startProfitWorkflow").addEventListener("click", async () => {
    try {
      const result = await post("/api/workflow/start", { workflow_id: "profitability_review" });
      toast(`Workflow started: ${result.run.run_id}`);
      refresh();
    } catch (error) {
      toast(error.message);
    }
  });
  $("#pauseTime").addEventListener("click", () => {
    state.paused = !state.paused;
    $("#pauseTime").textContent = state.paused ? "Resume Time" : "Pause Time";
  });
}

function wireModuleWindows() {
  document.querySelectorAll(".module-window").forEach((panel, index) => {
    if (panel.querySelector(":scope > .window-grip")) return;
    const grip = document.createElement("button");
    grip.type = "button";
    grip.className = "window-grip";
    const title = panel.dataset.moduleTitle || `Module ${index + 1}`;
    grip.innerHTML = `<span>${escapeHtml(title)}</span><b aria-hidden="true"><i></i><i></i></b>`;
    grip.setAttribute("aria-label", `Move ${title}`);
    panel.prepend(grip);

    let drag = null;
    grip.addEventListener("pointerdown", (event) => {
      if (event.clientX > grip.getBoundingClientRect().right - 46) return;
      drag = {
        id: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        x: Number(panel.dataset.x || 0),
        y: Number(panel.dataset.y || 0),
      };
      grip.setPointerCapture(event.pointerId);
      panel.classList.add("dragging");
    });
    grip.addEventListener("pointermove", (event) => {
      if (!drag || event.pointerId !== drag.id) return;
      const x = drag.x + event.clientX - drag.startX;
      const y = drag.y + event.clientY - drag.startY;
      panel.dataset.x = String(x);
      panel.dataset.y = String(y);
      panel.style.transform = `translate(${x}px, ${y}px)`;
    });
    grip.addEventListener("pointerup", () => {
      drag = null;
      panel.classList.remove("dragging");
    });
    grip.addEventListener("dblclick", () => {
      panel.dataset.x = "0";
      panel.dataset.y = "0";
      panel.style.transform = "";
    });
    grip.addEventListener("click", (event) => {
      if (event.clientX <= grip.getBoundingClientRect().right - 46) return;
      panel.classList.toggle("module-minimized");
    });
    grip.querySelector("b").addEventListener("click", (event) => {
      event.stopPropagation();
      panel.classList.toggle("module-minimized");
    });
  });
}

function tickClock() {
  if (!state.paused) {
    const now = new Date();
    $("#clock").textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
}

wireControls();
wireModuleWindows();
refresh().catch((error) => toast(error.message));
window.setInterval(() => refresh().catch(() => {}), 5000);
window.setInterval(tickClock, 1000);
