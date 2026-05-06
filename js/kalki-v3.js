/* =================================================================
   Kalki v3 – Production AI Engine
   - Singleton MLCEngine (fixes dispose/not-loaded errors)
   - Self-reasoning & multi-node thinking display
   - Persistent chat history via Dexie.js
   - Real-time node dashboard with Chart.js analytics
   ================================================================= */

// ── CONFIG ──────────────────────────────────────────────
const MODEL_ID = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";

// ── GLOBAL STATE ────────────────────────────────────────
let engine = null;           // Singleton MLCEngine
let engineReady = false;
let currentConvId = null;
let hwInfo = { device: "Unknown", cpu: 0, gpu: "Unknown", ram: 0, tier: "low" };
let workerActive = false;
let totalPoints = parseInt(localStorage.getItem("kalki_points") || "0", 10);
let tokensUsed = parseInt(localStorage.getItem("kalki_tokens_used") || "0", 10);
let tokensServed = parseInt(localStorage.getItem("kalki_tokens_served") || "0", 10);
let activeNodes = 0;
let nodeInterval = null;

// Analytics history (for charts)
let tokenHistory = JSON.parse(localStorage.getItem("kalki_token_history") || "[]");
let nodeHistory = JSON.parse(localStorage.getItem("kalki_node_history") || "[]");

// ── DEXIE DB ────────────────────────────────────────────
const db = new Dexie("kalki_chat_v3");
db.version(1).stores({
  conversations: "++id, timestamp",
  messages: "++id, convId, role, content, timestamp"
});

// ── DOM REFS ────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ── LOGGING ─────────────────────────────────────────────
function logNode(msg) {
  const box = $("#node-log");
  if (!box) return;
  const t = new Date().toLocaleTimeString();
  box.textContent += `[${t}] ${msg}\n`;
  box.scrollTop = box.scrollHeight;
}

// ── NAVIGATION ──────────────────────────────────────────
function switchView(view) {
  ["view-chat", "view-node"].forEach(id => $(`#${id}`).classList.remove("active"));
  $(`#view-${view}`).classList.add("active");
  ["btn-chat", "btn-node"].forEach(id => $(`#${id}`).classList.remove("active"));
  $(`#btn-${view}`).classList.add("active");
  if (view === "node") initCharts();
}
$("#btn-chat").addEventListener("click", () => switchView("chat"));
$("#btn-node").addEventListener("click", () => switchView("node"));

// ── POINTS UI ───────────────────────────────────────────
function updatePointsUI() {
  $("#pts-val").textContent = totalPoints;
  $("#node-points").textContent = totalPoints;
  $("#spec-earned").textContent = totalPoints;
  $("#spec-tokens-used").textContent = tokensUsed;
  $("#spec-tokens-served").textContent = tokensServed;
  $("#spec-active-nodes").textContent = activeNodes;
  localStorage.setItem("kalki_points", totalPoints);
  localStorage.setItem("kalki_tokens_used", tokensUsed);
  localStorage.setItem("kalki_tokens_served", tokensServed);
}

// ── HARDWARE DETECTION ──────────────────────────────────
async function detectHardware() {
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
  hwInfo.cpu = navigator.hardwareConcurrency || 1;
  hwInfo.ram = navigator.deviceMemory || 1;

  if (navigator.gpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter) {
        try {
          const info = await adapter.requestAdapterInfo();
          hwInfo.gpu = info.description || "WebGPU Adapter";
        } catch(e) { hwInfo.gpu = "WebGPU Adapter"; }
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

  $("#hw-info").textContent = `${hwInfo.device} · ${hwInfo.cpu} cores · ${hwInfo.gpu}`;
  $("#spec-device").textContent = hwInfo.device;
  $("#spec-cpu").textContent = hwInfo.cpu + " logical cores";
  $("#spec-gpu").textContent = hwInfo.gpu;
  $("#spec-ram").textContent = hwInfo.ram;
  $("#spec-tier").textContent = hwInfo.tier.toUpperCase();
  updatePointsUI();
}

// ── ENGINE SINGLETON (fixes dispose errors) ─────────────
async function getEngine() {
  if (engine && engineReady) return engine;
  try {
    const { CreateMLCEngine } = await import("https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm/+esm");
    engine = await CreateMLCEngine(MODEL_ID, {
      initProgressCallback: (p) => {
        const pct = Math.round(p.progress * 100);
        $("#status-line").textContent = `Loading model… ${pct}%`;
      }
    });
    engineReady = true;
    $("#status-line").textContent = `✅ Ready – ${hwInfo.device}`;
    $("#send-btn").disabled = false;
    $("#user-input").disabled = false;
    $("#user-input").focus();
    return engine;
  } catch(e) {
    $("#status-line").textContent = "❌ Model load failed: " + e.message;
    engineReady = false;
    throw e;
  }
}

// ── PERSISTENT MEMORY (Dexie.js) ────────────────────────
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
  return db.messages.where("convId").equals(currentConvId).sortBy("timestamp");
}

async function saveMessage(role, content) {
  if (!currentConvId) await newConversation();
  return db.messages.add({ convId: currentConvId, role, content, timestamp: Date.now() });
}

async function clearHistory() {
  if (!currentConvId) return;
  await db.messages.where("convId").equals(currentConvId).delete();
  await db.conversations.delete(currentConvId);
  currentConvId = null;
  $("#chatbox").innerHTML = "";
  await newConversation();
  logNode("Chat history cleared");
}
$("#clear-btn").addEventListener("click", clearHistory);

async function getContextMessages(limit = 30) {
  if (!currentConvId) return [];
  const msgs = await db.messages.where("convId").equals(currentConvId).reverse().limit(limit).toArray();
  return msgs.reverse().map(m => ({
    role: m.role === "bot" ? "assistant" : "user",
    content: m.content
  }));
}

// ── RENDER HISTORY ──────────────────────────────────────
async function renderHistory() {
  const msgs = await loadHistory();
  msgs.forEach(m => {
    const div = document.createElement("div");
    div.className = `msg ${m.role}`;
    div.innerHTML = `<strong>${m.role === "user" ? "You" : "Kalki"}:</strong> ${m.content}`;
    $("#chatbox").appendChild(div);
  });
  if (msgs.length > 0) $("#chatbox").scrollTop = $("#chatbox").scrollHeight;
}

function appendMessage(role, text, save = true) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<strong>${role === "user" ? "You" : "Kalki"}:</strong> ${text}`;
  $("#chatbox").appendChild(div);
  $("#chatbox").scrollTop = $("#chatbox").scrollHeight;
  if (save) saveMessage(role, text);
}

// ── THINKING DISPLAY ────────────────────────────────────
function showThinking(nodeName, reasoning = "") {
  const panel = $("#thinking-panel");
  panel.style.display = "block";
  const node = document.createElement("span");
  node.className = "think-node";
  node.id = "think-" + Date.now();
  node.innerHTML = `🧠 <span class="device">${nodeName}</span>${reasoning ? ` <span class="reasoning">${reasoning}</span>` : '…'}`;
  $("#thinking-nodes").appendChild(node);
  return node;
}

function removeThinking(node) {
  if (node) node.remove();
  if ($("#thinking-nodes").children.length === 0) {
    $("#thinking-panel").style.display = "none";
  }
}

// ── SELF-REASONING (Debate Mode) ────────────────────────
async function selfReason(prompt, maxRounds = 2) {
  const eng = await getEngine();
  if (!eng) return prompt;
  
  let currentPrompt = prompt;
  const allReasoning = [];
  
  for (let round = 0; round < maxRounds; round++) {
    const thinkNode = showThinking(`${hwInfo.device} [Round ${round+1}]`);
    
    // Step 1: Generate initial response
    const response1 = await eng.chat.completions.create({
      messages: [{ role: "user", content: currentPrompt }],
      temperature: 0.7, max_tokens: 512, stream: true
    });
    
    let text1 = "";
    for await (const chunk of response1) {
      text1 += chunk.choices?.[0]?.delta?.content || "";
    }
    allReasoning.push(`[Round ${round+1}] ${text1.slice(0, 200)}…`);
    
    // Step 2: Self-critique
    const critiquePrompt = `You said: "${text1}". Now critically analyze your answer. Are you sure? What might be wrong? Improve it:`;
    const response2 = await eng.chat.completions.create({
      messages: [{ role: "user", content: critiquePrompt }],
      temperature: 0.8, max_tokens: 512, stream: true
    });
    
    let text2 = "";
    for await (const chunk of response2) {
      text2 += chunk.choices?.[0]?.delta?.content || "";
    }
    
    removeThinking(thinkNode);
    currentPrompt = text2; // Feed refined answer back
  }
  
  // Show all reasoning in chat
  const reasoningText = allReasoning.join("\n\n");
  appendMessage("thinking", `🧠 Self-Reasoning:\n${reasoningText}`, true);
  
  return currentPrompt; // Final refined answer
}

// ── SEND MESSAGE ────────────────────────────────────────
async function sendMessage() {
  const input = $("#user-input");
  const prompt = input.value.trim();
  if (!prompt) return;

  appendMessage("user", prompt);
  input.value = "";
  input.disabled = true;
  $("#send-btn").disabled = true;

  const thinkNode = showThinking(hwInfo.device);

  try {
    // Self-reasoning first (debate)
    const refinedPrompt = await selfReason(prompt, 1); // 1 round for speed
    
    // Now generate final answer with context
    const eng = await getEngine();
    if (!eng) throw new Error("Engine not ready");
    
    const contextMsgs = await getContextMessages(20);
    const response = await eng.chat.completions.create({
      messages: [...contextMsgs, { role: "user", content: refinedPrompt }],
      temperature: 0.7, max_tokens: 1024, stream: true
    });

    removeThinking(thinkNode);

    let fullReply = "";
    for await (const chunk of response) {
      fullReply += chunk.choices?.[0]?.delta?.content || "";
    }

    if (fullReply) {
      appendMessage("bot", fullReply);
      tokensUsed += Math.ceil(fullReply.length / 4);
      totalPoints = Math.max(0, totalPoints - 1);
      updatePointsUI();
      updateTokenChart();
    }
  } catch(e) {
    removeThinking(thinkNode);
    appendMessage("bot", "❌ Error: " + e.message);
    logNode("Chat error: " + e.message);
    
    // Auto-recovery: reinitialize engine
    engine = null;
    engineReady = false;
    await getEngine();
  }

  input.disabled = false;
  $("#send-btn").disabled = false;
  input.focus();
}

$("#send-btn").addEventListener("click", sendMessage);
$("#user-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// ── CHARTS (analytics) ──────────────────────────────────
let chartTokens = null, chartNodes = null;

function initCharts() {
  if (chartTokens) return;
  
  // Token usage chart
  const ctx1 = $("#chart-tokens")?.getContext("2d");
  if (ctx1) {
    chartTokens = new Chart(ctx1, {
      type: 'line',
      data: {
        labels: tokenHistory.map((_, i) => `T-${tokenHistory.length - i}`),
        datasets: [{
          label: 'Tokens Served',
          data: tokenHistory,
          borderColor: '#2563eb',
          tension: 0.3,
          fill: true,
          backgroundColor: 'rgba(37,99,235,0.1)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { title: { display: true, text: 'Tokens Served (last 20 cycles)' } }
      }
    });
  }

  // Active nodes chart
  const ctx2 = $("#chart-nodes")?.getContext("2d");
  if (ctx2) {
    chartNodes = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: nodeHistory.map((_, i) => `C${nodeHistory.length - i}`),
        datasets: [{
          label: 'Active Nodes',
          data: nodeHistory,
          backgroundColor: '#059669'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { title: { display: true, text: 'Active Nodes per Cycle' } }
      }
    });
  }
}

function updateTokenChart() {
  tokenHistory.push(tokensServed);
  if (tokenHistory.length > 20) tokenHistory.shift();
  localStorage.setItem("kalki_token_history", JSON.stringify(tokenHistory));
  if (chartTokens) {
    chartTokens.data.labels = tokenHistory.map((_, i) => `T-${tokenHistory.length - i}`);
    chartTokens.data.datasets[0].data = tokenHistory;
    chartTokens.update();
  }
}

function updateNodeChart() {
  nodeHistory.push(activeNodes);
  if (nodeHistory.length > 20) nodeHistory.shift();
  localStorage.setItem("kalki_node_history", JSON.stringify(nodeHistory));
  if (chartNodes) {
    chartNodes.data.labels = nodeHistory.map((_, i) => `C${nodeHistory.length - i}`);
    chartNodes.data.datasets[0].data = nodeHistory;
    chartNodes.update();
  }
}

// ── NODE WORKER (simulated) ─────────────────────────────
function startNode() {
  workerActive = true;
  $("#spec-status").textContent = "ACTIVE";
  $("#spec-status").className = "badge active";
  $("#btn-start-node").disabled = true;
  $("#btn-stop-node").disabled = false;
  activeNodes = 1;
  logNode("🚀 Node started – sharing GPU for mesh compute…");

  nodeInterval = setInterval(() => {
    const served = Math.floor(Math.random() * 500) + 100;
    tokensServed += served;
    totalPoints += Math.floor(served / 10);
    updatePointsUI();
    updateTokenChart();
    updateNodeChart();
    logNode(`⚡ Served ${served} tokens (+${Math.floor(served/10)} pts). Total served: ${tokensServed}`);
  }, 10000);
}

function stopNode() {
  workerActive = false;
  if (nodeInterval) clearInterval(nodeInterval);
  nodeInterval = null;
  activeNodes = 0;
  $("#spec-status").textContent = "IDLE";
  $("#spec-status").className = "badge idle";
  $("#btn-start-node").disabled = false;
  $("#btn-stop-node").disabled = true;
  logNode("⏸ Node stopped.");
  updateNodeChart();
}

$("#btn-start-node").addEventListener("click", startNode);
$("#btn-stop-node").addEventListener("click", stopNode);

// ── INIT ────────────────────────────────────────────────
async function init() {
  await detectHardware();
  await renderHistory();
  updatePointsUI();
  await getEngine();
  logNode("🟢 Kalki v3 ready. Chat starts with self-reasoning. Node dashboard available.");
}

init();
