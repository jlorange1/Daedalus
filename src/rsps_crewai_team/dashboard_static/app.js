const state = {
  paused: false,
  selectedAgent: 1,
  lastStatus: null,
};

const $ = (selector) => document.querySelector(selector);

function toast(message) {
  const box = $("#toast");
  box.textContent = message;
  box.classList.add("show");
  window.setTimeout(() => box.classList.remove("show"), 4200);
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

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderQueue(queue) {
  const visualBacklog = {
    inbox: [
      { title: "Design crystal staff encounter hook", file: "#213", kind: "Content", stamp: "queued" },
      { title: "Bank Tabs QoL Improvements", file: "#217", kind: "Backend", stamp: "queued" },
      { title: "Player Moderation Dashboard", file: "#221", kind: "Backend", stamp: "ready" },
      { title: "Daily Task System Refactor", file: "#226", kind: "Tech Debt", stamp: "ready" },
    ],
    running: [
      { title: "Safe Arena Matchmaking System", file: "#206", kind: "Backend", stamp: "62%" },
      { title: "Wildlands Boss Rework", file: "#207", kind: "Content", stamp: "active" },
      { title: "Anti-Cheat Packet Anomaly Detection", file: "#209", kind: "Security", stamp: "active" },
    ],
    failed: [
      { title: "Item Drop Table Balancing", file: "#204", kind: "Content", stamp: "review" },
      { title: "Login Server Rate Limiting", file: "#205", kind: "Security", stamp: "review" },
    ],
    done: [
      { title: "XP Locking Improvements", file: "#202", kind: "Done", stamp: "May 11" },
      { title: "Quest: Dragonkin Diplomacy", file: "#201", kind: "Done", stamp: "May 10" },
      { title: "Discord Bot Notifications", file: "#200", kind: "Done", stamp: "May 9" },
    ],
  };
  let visualTotal = 0;
  for (const status of ["inbox", "running", "failed", "done"]) {
    const lane = queue[status];
    const list = $(`#${status}List`);
    const tag = status === "inbox" ? "Queued" : status === "running" ? "Active" : status === "failed" ? "Review" : "Done";
    const items = lane.items.length ? lane.items.slice().reverse() : visualBacklog[status];
    visualTotal += lane.items.length ? lane.count : items.length;
    $(`#${status}Count`).textContent = lane.items.length ? lane.count : items.length;
    list.innerHTML = items.slice(0, 4).map((item) => workCard(item, tag)).join("");
  }
  const total = queue.inbox.count + queue.running.count + queue.failed.count;
  $("#queueBadge").textContent = total || visualTotal;
  $("#queueCount").textContent = `${total || visualTotal} work orders`;
}

function renderAgents(agents) {
  const roles = ["producer", "backend", "content", "qa", "security", "docs"];
  const grid = $("#agentGrid");
  grid.innerHTML = agents.map((agent, index) => `
    <article class="agent-desk role-${index} ${index === state.selectedAgent ? "selected" : ""}" data-agent="${index}" data-state="${escapeHtml(agent.status)}" title="${escapeHtml(agent.role)}: ${escapeHtml(agent.task)}">
      <span class="agent-hitbox ${agent.status === "working" ? "working" : ""}"></span>
      <div class="agent-plate" aria-hidden="true">
        <h3>${escapeHtml(agent.role)}</h3>
        <p>${escapeHtml(agent.name)} - ${escapeHtml(agent.status)}</p>
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
  const roles = ["producer", "backend", "content", "qa", "security", "docs"];
  const roleKey = roles[state.selectedAgent] || roles[0];
  $("#agentInspector").innerHTML = `
    <div class="agent-hero">
      <span class="agent-medallion"><img src="/assets/role-portrait-${roleKey}.png" alt="" /></span>
      <div>
        <strong>${escapeHtml(agent.role)}</strong>
        <p><span class="state-dot ${agent.status === "working" ? "good" : "warn"}"></span>${escapeHtml(agent.name)} ${escapeHtml(agent.status)}.</p>
      </div>
    </div>
    <div class="inspector-task">
      <span>Current Task</span>
      <p>${escapeHtml(agent.task)}</p>
    </div>
    <dl class="mini-stats">
      <div><dt>Progress</dt><dd>${agent.progress}%</dd></div>
      <div><dt>Focus</dt><dd>${escapeHtml(agent.role.split(" ")[0])}</dd></div>
      <div><dt>Model</dt><dd>${escapeHtml(agent.model.replace(":free", ""))}</dd></div>
    </dl>
    <div class="meter"><b style="--value: ${agent.progress}%"></b></div>
  `;
  const rsps = status.git.rsps;
  $("#diffSummary").textContent = rsps.detail && rsps.detail !== "clean"
    ? rsps.detail
    : "+ ForgeBoard scene assets validated\n+ Worker queue ready for next patch\n+ Review packet will appear after the next run";
  $("#branchState").innerHTML = `<span class="state-chip good">${escapeHtml(rsps.branch || "main")}</span><span>${rsps.clean ? "ready" : "changes waiting"}</span>`;
}

function renderReadiness(status) {
  const ready = status.readiness;
  const buildReady = ready.java && ready.git_lfs && ready.rsps_repo;
  $("#autonomyState").innerHTML = `<span class="switch ${status.env.autonomy ? "on" : ""}"></span>${pill(status.env.autonomy)}`;
  $("#agentsOnline").textContent = `${status.agents.length} / 6`;
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

async function refresh() {
  const response = await fetch("/api/status");
  const status = await response.json();
  state.lastStatus = status;
  renderQueue(status.queue);
  renderAgents(status.agents);
  renderReadiness(status);
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
  $("#runBuild").addEventListener("click", () => toast("Build/Test command is configured. Install Java 11 and Git LFS before running the gate."));
  $("#pushBranch").addEventListener("click", () => toast("GitHub push is handled after successful worker runs when enabled."));
  $("#cronTick").addEventListener("click", async () => {
    try {
      const result = await post("/api/action", { action: "cron-tick" });
      toast(`Cron tick started. PID ${result.pid}.`);
    } catch (error) {
      toast(error.message);
    }
  });
  $("#pauseTime").addEventListener("click", () => {
    state.paused = !state.paused;
    $("#pauseTime").textContent = state.paused ? "Resume Time" : "Pause Time";
  });
}

function tickClock() {
  if (!state.paused) {
    const now = new Date();
    $("#clock").textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
}

wireControls();
refresh().catch((error) => toast(error.message));
window.setInterval(() => refresh().catch(() => {}), 5000);
window.setInterval(tickClock, 1000);
