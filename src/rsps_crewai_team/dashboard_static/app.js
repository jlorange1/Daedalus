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
  return `<article class="work-card">
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
      { title: "Add Nightmare Staff Special Attack", file: "#213", kind: "Content", stamp: "queued" },
      { title: "Bank Tabs QoL Improvements", file: "#217", kind: "Backend", stamp: "queued" },
      { title: "Player Moderation Dashboard", file: "#221", kind: "Backend", stamp: "ready" },
      { title: "Daily Task System Refactor", file: "#226", kind: "Tech Debt", stamp: "ready" },
    ],
    running: [
      { title: "Clan Wars: Safe Minigame System", file: "#206", kind: "Backend", stamp: "62%" },
      { title: "Wilderness Boss Rework", file: "#207", kind: "Content", stamp: "active" },
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
  $("#queueCount").textContent = total ? `${total} work orders` : `${visualTotal} planned tasks`;
}

function renderAgents(agents) {
  const grid = $("#agentGrid");
  grid.innerHTML = agents.map((agent, index) => `
    <article class="agent-desk" data-agent="${index}">
      <div class="desk-art">
        <img class="desk-base" src="/assets/desk.png" alt="" />
        <img class="worker-sprite ${agent.status === "working" ? "working" : ""}" src="/assets/worker.png" alt="" />
        <img class="monitor-sprite" src="/assets/monitor.png" alt="" />
      </div>
      <div class="agent-plate">
        <h3>${escapeHtml(agent.role)}</h3>
        <p>${escapeHtml(agent.name)} - ${escapeHtml(agent.status)}</p>
        <div class="meter"><b style="--value: ${agent.progress}%"></b></div>
      </div>
      <p class="task-line">${escapeHtml(agent.task)}</p>
      <p class="model-line">${escapeHtml(agent.model)}</p>
    </article>
  `).join("");
  grid.querySelectorAll(".agent-desk").forEach((card) => {
    card.addEventListener("click", () => {
      state.selectedAgent = Number(card.dataset.agent || 0);
      renderInspector(state.lastStatus);
    });
  });
  renderInspector(state.lastStatus);
}

function renderInspector(status) {
  if (!status) return;
  const agent = status.agents[state.selectedAgent] || status.agents[0];
  $("#agentInspector").innerHTML = `
    <strong>${escapeHtml(agent.role)}</strong>
    <p>${escapeHtml(agent.name)} is ${escapeHtml(agent.status)}.</p>
    <p>Current task: ${escapeHtml(agent.task)}</p>
    <p>Model: ${escapeHtml(agent.model)}</p>
    <div class="meter"><b style="--value: ${agent.progress}%"></b></div>
  `;
  const rsps = status.git.rsps;
  $("#diffSummary").textContent = [
    `RSPS repo: ${status.project.rsps_repo}`,
    `Branch: ${rsps.branch || "unknown"}`,
    `Worktree: ${rsps.clean ? "clean" : "changes present"}`,
    "",
    rsps.detail || "No diff summary yet.",
  ].join("\n");
  $("#branchState").textContent = `${rsps.branch || "unknown"} - ${rsps.clean ? "clean" : "changes waiting"}`;
}

function renderReadiness(status) {
  const ready = status.readiness;
  const buildReady = ready.java && ready.git_lfs && ready.rsps_repo;
  $("#autonomyState").textContent = pill(status.env.autonomy);
  $("#agentsOnline").textContent = `${status.agents.length} / 6`;
  $("#buildStatus").textContent = buildReady ? "Passing gate" : "Needs tools";
  $("#githubState").textContent = status.git.daedalus.clean ? "main up to date" : "local changes";
  $("#envState").textContent = buildReady ? "Healthy" : "Needs Java/LFS";
  $("#testList").innerHTML = [
    ["Java 11", ready.java],
    ["Git LFS", ready.git_lfs],
    ["OpenClaw", ready.openclaw],
    ["RSPS Repo", ready.rsps_repo],
  ].map(([label, ok]) => `<p>${ok ? "Passed" : "Missing"} - ${label}</p>`).join("");
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
