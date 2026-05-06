/*
 * Kalki Worker – Performs a small WebGPU compute task and reports via
 * GitHub issues. Points are tracked in the repo’s tasks.json.
 */
const OWNER = "CodeWander-666";    // <-- CHANGE ME
const REPO = "kalkicore";                 // <-- CHANGE ME if needed

let workerActive = false;
let points = 0;

// Load points from local/session storage + remote
async function loadPoints() {
  // In a real system, points are read from tasks.json.
  // For now, we keep a local counter.
  const saved = parseInt(localStorage.getItem("kalki_points") || "0", 10);
  points = saved;
  updateUI();
}

function updateUI() {
  document.getElementById("points-display").textContent = `${points} points`;
}

async function submitResult(taskId, proof) {
  const title = `[worker-result] ${taskId}`;
  const body = `\`\`\`json\n${JSON.stringify(proof)}\n\`\`\``;
  // Anonymous issue creation on a public repo (no token needed)
  await fetch(`https://api.github.com/repos/${OWNER}/${REPO}/issues`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, body, labels: ["worker-result"] }),
  });
}

async function startWorker() {
  workerActive = true;
  document.getElementById("start-btn").disabled = true;
  document.getElementById("stop-btn").disabled = false;
  log("Worker started. Waiting for tasks…");

  // Poll tasks.json every 10 seconds
  while (workerActive) {
    try {
      const resp = await fetch(
        `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/tasks.json`
      );
      const tasks = await resp.json();
      const pending = tasks.pending || [];
      if (pending.length > 0) {
        const task = pending[0]; // take first
        log(`Processing task ${task.id}…`);
        // Simulate compute (in production, run real WebGPU shader)
        const proof = { taskId: task.id, hash: "dummy-hash", timestamp: Date.now() };
        await submitResult(task.id, proof);
        // Optimistically add points
        points += 10;
        localStorage.setItem("kalki_points", points);
        updateUI();
        log(`Task ${task.id} completed. +10 points`);
      }
    } catch (e) {
      log("Fetch error: " + e.message);
    }
    await new Promise((r) => setTimeout(r, 10000));
  }
}

function stopWorker() {
  workerActive = false;
  document.getElementById("start-btn").disabled = false;
  document.getElementById("stop-btn").disabled = true;
  log("Worker stopped.");
}

function log(msg) {
  const el = document.getElementById("log");
  el.textContent += msg + "\n";
}

loadPoints();
window.startWorker = startWorker;
window.stopWorker = stopWorker;
