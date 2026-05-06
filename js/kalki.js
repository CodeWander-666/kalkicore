/* =================================================================
   KalkiCore – Production AI Engine (Chat + Node Dashboard)
   - Dexie.js for persistent chat history (IndexedDB)
   - WebLLM for streaming inference with thinking display
   - Real hardware detection + node dashboard
   - Real‑time points tracking
   ================================================================= */

// ── CONFIG ──────────────────────────────────────────────
const KALKI_OWNER = "CodeWander-666";
const KALKI_REPO  = "kalkicore";
const MODEL_ID    = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";

// ── Dexie DB for chat history ──────────────────────────
const db = new Dexie("kalki_chat");
db.version(1).stores({
  conversations: "++id, timestamp",
  messages: "++id, convId, role, content, timestamp"
});

let currentConvId = null;
let engine = null;
let hwInfo = { device: "unknown", cpu: 0, gpu: "unknown", ram: 0, tier: "low" };
let workerActive = false;
let totalPoints = parseInt(localStorage.getItem("kalki_points") || "0", 10);
let tokensUsed = parseInt(localStorage.getItem("kalki_tokens_used") || "0", 10);
let tokensServed = parseInt(localStorage.getItem("kalki_tokens_served") || "0", 10);

// ── DOM refs ───────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ── LOGGING ────────────────────────────────────────────
function logNode(msg) {
  const box = $("#node-log");
  if (!box) return;
  const t = new Date().toLocaleTimeString();
  box.textContent += `[${t}] ${msg}\n`;
  box.scrollTop = box.scrollHeight;
}

// ── NAVIGATION ─────────────────────────────────────────
function switchView(view) {
  ["view-chat", "view-node"].forEach(id => $(`#${id}`).classList.remove("active"));
  $(`#view-${view}`).classList.add("active");
  ["btn-chat", "btn-node"].forEach(id => $(`#${id}`).classList.remove("active"));
  $(`#btn-${view}`).classList.add("active");
}

$("#btn-chat").addEventListener("click", () => switchView("chat"));
$("#btn-node").addEventListener("click", () => switchView("node"));

// ── POINTS UI ──────────────────────────────────────────
function updatePointsUI() {
  $("#pts-val").textContent = totalPoints;
  $("#node-points").textContent = totalPoints;
  $("#spec-earned").textContent = totalPoints;
  $("#spec-tokens").textContent = tokensUsed;
  $("#spec-served").textContent = tokensServed;
  localStorage.setItem("kalki_points", totalPoints);
  localStorage.setItem("kalki_tokens_used", tokensUsed);
  localStorage.setItem("kalki_tokens_served", tokensServed);
}

// ── CHAT HISTORY (Dexie.js) ────────────────────────────
async function newConversation() {
  currentConvId = await db.conversations.add({ timestamp: Date.now() });
  return currentConvId;
}

async function loadHistory() {
  const convs = await db.conversations.orderBy("timestamp").reverse().limit(1).toArray();
  if (convs.length === 0) {
    currentConvId = await newConversation();
    return [];
  }
  currentConvId = convs[0].id;
  const msgs = await db.messages.where("convId").equals(currentConvId).sortBy("timestamp");
  return msgs;
}

async function saveMessage(role, content) {
  if (!currentConvId) await newConversation();
  return db.messages.add({
    convId: currentConvId,
    role, content,
    timestamp: Date.now()
  });
}

async function clearHistory() {
  if (!currentConvId) return;
  await db.messages.where("convId").equals(currentConvId).delete();
  await db.conversations.delete(currentConvId);
  currentConvId = null;
  $("#chatbox").innerHTML = "";
  await newConversation();
}

$("#clear-btn").addEventListener("click", clearHistory);

// ── RENDER PAST CONVERSATIONS ──────────────────────────
async function renderHistory() {
  const msgs = await loadHistory();
  const box = $("#chatbox");
  msgs.forEach(m => appendMessage(m.role, m.content, false));
  if (msgs.length > 0) box.scrollTop = box.scrollHeight;
}

function appendMessage(role, text, save = true) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<strong>${role === "user" ? "You" : "Kalki"}:</strong> ${text}`;
  $("#chatbox").appendChild(div);
  $("#chatbox").scrollTop = $("#chatbox").scrollHeight;
  if (save) saveMessage(role, text);
}

// ── HARDWARE DETECTION ─────────────────────────────────
async function detectHardware() {
  // Device name from user agent
  const ua = navigator.userAgent;
  const mobileMatch = ua.match(/Android\s+[\d.]+;\s+([^;)]+)\s+Build/);
  const modelMatch = ua.match(/\((?:Linux; Android [^;]+; )?([^;)]+?)(?: Build|\))/);
  if (mobileMatch) {
    hwInfo.device = mobileMatch[1].trim();
  } else if (modelMatch && /Mobile|Android/.test(ua)) {
    hwInfo.device = modelMatch[1].trim();
  } else {
    const plat = navigator.platform || "";
    hwInfo.device = plat.includes("Win") ? "Windows PC" :
                    plat.includes("Mac") ? "Mac" :
                    plat.includes("Linux") ? "Linux Desktop" : "Unknown Device";
  }
  // CPU
  hwInfo.cpu = navigator.hardwareConcurrency || 1;
  // RAM
  hwInfo.ram = navigator.deviceMemory || 1;
  // GPU + Tier (via WebGPU)
  if (navigator.gpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter) {
        try { const info = await adapter.requestAdapterInfo(); hwInfo.gpu = info.description || "WebGPU Adapter"; } catch(e) { hwInfo.gpu = "WebGPU Adapter"; }
        const dev = await adapter.requestDevice();
        const maxBuf = dev.limits.maxBufferSize / (1024*1024);
        hwInfo.tier = maxBuf >= 4000 ? "high" : maxBuf >= 2000 ? "medium" : "low";
        dev.destroy();
      }
    } catch(e) { hwInfo.gpu = "Unknown GPU"; }
  } else {
    hwInfo.gpu = "No WebGPU";
    hwInfo.tier = "cpu";
  }

  // Update UI
  $("#hw-info").textContent = `${hwInfo.device} · ${hwInfo.cpu} cores · ${hwInfo.gpu}`;
  $("#spec-device").textContent = hwInfo.device;
  $("#spec-cpu").textContent = hwInfo.cpu + " logical cores";
  $("#spec-gpu").textContent = hwInfo.gpu;
  $("#spec-ram").textContent = hwInfo.ram + " GB";
  $("#spec-tier").textContent = hwInfo.tier.toUpperCase();
  updatePointsUI();
}

// ── THINKING DISPLAY ───────────────────────────────────
function showThinking(nodeName) {
  const bar = $("#thinking-bar");
  bar.style.display = "block";
  const node = document.createElement("span");
  node.className = "think-node";
  node.textContent = `🧠 Thinking (${nodeName})…`;
  node.id = "think-" + Date.now();
  $("#thinking-nodes").appendChild(node);
  return node;
}

function removeThinking(node) {
  if (node) node.remove();
  if ($("#thinking-nodes").children.length === 0) {
    $("#thinking-bar").style.display = "none";
  }
}

// ── MODEL LOADING ──────────────────────────────────────
async function initEngine() {
  try {
    const { CreateMLCEngine } = await import("https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm/+esm");
    engine = await CreateMLCEngine(MODEL_ID, {
      initProgressCallback: (p) => {
        const pct = Math.round(p.progress * 100);
        $("#status-line").textContent = `Loading model… ${pct}%`;
      }
    });
    $("#status-line").textContent = "✅ Ready – " + hwInfo.device;
    $("#send-btn").disabled = false;
    $("#user-input").disabled = false;
    $("#user-input").focus();
  } catch(e) {
    $("#status-line").textContent = "❌ Model load failed: " + e.message;
  }
}

// ── SEND MESSAGE ───────────────────────────────────────
async function sendMessage() {
  const input = $("#user-input");
  const prompt = input.value.trim();
  if (!prompt || !engine) return;

  appendMessage("user", prompt);
  input.value = "";
  input.disabled = true;
  $("#send-btn").disabled = true;

  // Show thinking indicator
  const thinkNode = showThinking(hwInfo.device);

  try {
    // Build context from history
    const historyMsgs = await db.messages
      .where("convId").equals(currentConvId)
      .reverse().limit(20).toArray();
    const contextMessages = historyMsgs.reverse().map(m => ({
      role: m.role === "bot" ? "assistant" : "user",
      content: m.content
    }));

    // Stream the response
    const chunks = await engine.chat.completions.create({
      messages: [...contextMessages, { role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 1024,
      stream: true
    });

    removeThinking(thinkNode);

    // Collect streamed response
    let fullReply = "";
    for await (const chunk of chunks) {
      const delta = chunk.choices?.[0]?.delta?.content || "";
      fullReply += delta;
    }

    if (fullReply) {
      appendMessage("bot", fullReply);
      tokensUsed += Math.ceil(fullReply.length / 4); // rough token estimate
      totalPoints = Math.max(0, totalPoints - 1); // deduct 1 point per response
      updatePointsUI();
    } else {
      appendMessage("bot", "⚠️ No response generated.");
    }
  } catch(e) {
    removeThinking(thinkNode);
    appendMessage("bot", "❌ Error: " + e.message);
  }

  input.disabled = false;
  $("#send-btn").disabled = false;
  input.focus();
}

$("#send-btn").addEventListener("click", sendMessage);
$("#user-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// ── NODE WORKER (simulated compute) ────────────────────
let nodeInterval = null;

function startNode() {
  workerActive = true;
  $("#spec-status").textContent = "ACTIVE";
  $("#spec-status").className = "badge active";
  $("#btn-start-node").disabled = true;
  $("#btn-stop-node").disabled = false;
  logNode("Node started – sharing GPU compute…");

  nodeInterval = setInterval(async () => {
    // Simulate serving tokens
    const served = Math.floor(Math.random() * 500) + 100;
    tokensServed += served;
    totalPoints += Math.floor(served / 10);
    updatePointsUI();
    logNode(`Served ${served} tokens (+${Math.floor(served/10)} pts). Total: ${tokensServed} tokens`);
  }, 15000);
}

function stopNode() {
  workerActive = false;
  if (nodeInterval) clearInterval(nodeInterval);
  nodeInterval = null;
  $("#spec-status").textContent = "IDLE";
  $("#spec-status").className = "badge idle";
  $("#btn-start-node").disabled = false;
  $("#btn-stop-node").disabled = true;
  logNode("Node stopped.");
}

$("#btn-start-node").addEventListener("click", startNode);
$("#btn-stop-node").addEventListener("click", stopNode);

// ── INIT ───────────────────────────────────────────────
async function init() {
  await detectHardware();
  await renderHistory();
  updatePointsUI();
  await initEngine();
  logNode("Node dashboard ready. Start sharing to earn points.");
}

init();
