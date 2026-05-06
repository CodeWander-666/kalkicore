/* ==========================================================================
   KalkiChat – Universal, production‑ready AI client
   - Imports WebLLM correctly
   - Safe GPU detection (handles missing requestAdapterInfo)
   - Loads the tiny Qwen2.5‑0.5B model (<1 GB, works everywhere)
   ========================================================================== */

import { CreateMLCEngine } from "https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm/+esm";

const TINY_MODEL = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";

/*************** DOM elements ***************/
const elHardware   = document.getElementById("detected-hardware");
const elModelStatus= document.getElementById("model-status");
const elPointsDisp = document.getElementById("points-display");
const elPointsVal  = document.getElementById("points-value");
const elWorkerMsg  = document.getElementById("worker-msg");
const chatbox      = document.getElementById("chatbox");
const inputEl      = document.getElementById("user-input");
const sendBtn      = document.getElementById("send-btn");
const logbox       = document.getElementById("logbox");

let engine = null;
let hwInfo = { name: "unknown", memoryMB: 0, tier: "unknown" };

/*************** Logging ***************/
function log(msg, toConsole = true) {
  const time = new Date().toLocaleTimeString();
  const line = `[${time}] ${msg}`;
  logbox.textContent += line + "\n";
  logbox.scrollTop = logbox.scrollHeight;
  if (toConsole) console.log(line);
}

/*************** Points (optional) ***************/
function updatePointsUI() {
  const pts = parseInt(localStorage.getItem("kalki_points") || "0", 10);
  if (pts > 0) {
    elPointsDisp.style.display = "inline-flex";
    elPointsVal.textContent = pts;
  }
}

/*************** Hardware detection (safe) ***************/
async function detectHardware() {
  log("🔍 Starting hardware detection…");
  if (!navigator.gpu) {
    log("⚠️ WebGPU NOT supported.");
    elHardware.textContent = "WebGPU unavailable – please use Chrome/Edge.";
    hwInfo.tier = "cpu";
    return hwInfo;
  }

  try {
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
      log("⚠️ No GPU adapter found.");
      elHardware.textContent = "No GPU adapter – AI cannot run.";
      hwInfo.tier = "cpu";
      return hwInfo;
    }

    // Try to get adapter info (may fail on older browsers)
    let adapterInfo = {};
    try {
      // Chrome 113+ has requestAdapterInfo()
      if (typeof adapter.requestAdapterInfo === "function") {
        adapterInfo = await adapter.requestAdapterInfo();
        hwInfo.name = adapterInfo.description || "WebGPU Adapter";
        hwInfo.architecture = adapterInfo.architecture || "";
      } else {
        // Fallback – just use generic name
        hwInfo.name = "WebGPU Adapter";
      }
    } catch (infoErr) {
      log("   ⚠️ Could not fetch adapter info: " + infoErr.message);
      hwInfo.name = "WebGPU Adapter";
    }

    log(`   ✅ Adapter found: ${hwInfo.name}`);

    // Estimate memory (crude, but safe)
    const memMatch = (hwInfo.name || "").match(/(\d+)\s*(GB|MB)/i);
    if (memMatch) {
      let mem = parseInt(memMatch[1], 10);
      if (memMatch[2].toUpperCase() === "GB") mem *= 1024;
      hwInfo.memoryMB = mem;
    }

    // Try to get device limits for more accurate memory
    try {
      const device = await adapter.requestDevice();
      const limits = device.limits;
      if (limits.maxBufferSize) {
        const bufMB = Math.floor(limits.maxBufferSize / (1024 * 1024));
        log(`   Max buffer size: ${bufMB} MB`);
        hwInfo.memoryMB = Math.max(hwInfo.memoryMB || 0, bufMB);
      }
      device.destroy();
    } catch (devErr) {
      log("   ❌ Could not probe device limits: " + devErr.message);
    }

    hwInfo.tier = hwInfo.memoryMB >= 4000 ? "high" : hwInfo.memoryMB >= 2000 ? "medium" : "low";
    elHardware.textContent = `🖥️ ${hwInfo.name} (${hwInfo.tier} tier, ~${hwInfo.memoryMB} MB)`;
    log(`   Hardware tier: ${hwInfo.tier}`);
  } catch (e) {
    log("❌ Detection error: " + e.message);
    elHardware.textContent = "Detection failed – see log.";
    hwInfo.tier = "cpu";
  }
  return hwInfo;
}

/*************** Model loading (only tiny) ***************/
async function loadTinyModel() {
  elModelStatus.textContent = "Loading tiny model (Qwen2.5‑0.5B)…";
  log("📦 Loading model: " + TINY_MODEL);
  inputEl.disabled = true;
  sendBtn.disabled = true;

  try {
    engine = await CreateMLCEngine(TINY_MODEL, {
      initProgressCallback: (p) => {
        const pct = Math.round(p.progress * 100);
        elModelStatus.textContent = `Loading model… ${pct}%`;
        log(`   Progress: ${pct}%`, false);
      }
    });
    elModelStatus.textContent = `✅ Ready – Qwen2.5‑0.5B`;
    log("✅ Model loaded successfully.");
    inputEl.disabled = false;
    sendBtn.disabled = false;
    localStorage.setItem("kalki_last_model", TINY_MODEL);
  } catch (err) {
    log("❌ Model load failed: " + err.message);
    elModelStatus.textContent = "❌ Model load failed – try a different browser or device.";
  }
}

/*************** Chat logic (unchanged) ***************/
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<strong>${role === "user" ? "You" : "Kalki"}:</strong> ${text}`;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}

async function handleSend() {
  const prompt = inputEl.value.trim();
  if (!prompt || !engine) return;

  appendMessage("user", prompt);
  inputEl.value = "";
  inputEl.disabled = true;
  sendBtn.disabled = true;

  log(`💬 User: ${prompt}`);
  try {
    const reply = await engine.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 1024,
    });
    const answer = reply.choices[0]?.message?.content || "(no response)";
    appendMessage("bot", answer);
    log(`🤖 Kalki: ${answer.slice(0, 80)}${answer.length > 80 ? '…' : ''}`);
  } catch (e) {
    appendMessage("bot", "⚠️ Error: " + e.message);
    log("❌ Chat error: " + e.message);
  }

  inputEl.disabled = false;
  sendBtn.disabled = false;
  inputEl.focus();
}

/*************** Initialization ***************/
async function init() {
  log("🟢 KalkiChat started");

  await detectHardware();
  await loadTinyModel();

  updatePointsUI();
  // Optional: fetch pending tasks from kalkicore (if you have cross‑repo access)
  setInterval(updatePointsUI, 30000);

  log("🟢 Initialization complete.");
}

sendBtn.addEventListener("click", handleSend);
inputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") handleSend();
});

init();
