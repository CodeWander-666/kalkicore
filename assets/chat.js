/*
 * Kalki Chat – Loads DeepSeek‑R1 via WebLLM and runs fully client‑side.
 * Model weights are cached in IndexedDB after first download.
 */
import { CreateMLCEngine } from "https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm/+esm";

const MODEL = "DeepSeek-R1-Distill-Qwen-1.5B-q4f16_1-MLC";
const chatbox = document.getElementById("chatbox");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const statusEl = document.getElementById("model-status");

let engine;

async function init() {
  try {
    engine = await CreateMLCEngine(MODEL, {
      initProgressCallback: (p) => {
        statusEl.textContent = `Loading model… ${Math.round(p.progress * 100)}%`;
      }
    });
    statusEl.textContent = "✅ Ready – unlimited free tokens!";
    input.disabled = false;
    sendBtn.disabled = false;
  } catch (e) {
    statusEl.textContent = "❌ Model load failed. Check WebGPU support (Chrome/Edge).";
    console.error(e);
  }
}

function appendChat(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<strong>${role === "user" ? "You" : "Kalki"}:</strong> ${text}`;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}

async function handleSend() {
  const prompt = input.value.trim();
  if (!prompt || !engine) return;
  appendChat("user", prompt);
  input.value = "";
  sendBtn.disabled = true;
  input.disabled = true;
  try {
    const reply = await engine.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 1024,
    });
    const answer = reply.choices[0]?.message?.content || "(no response)";
    appendChat("bot", answer);
  } catch (e) {
    appendChat("bot", "⚠️ Error: " + e.message);
  }
  sendBtn.disabled = false;
  input.disabled = false;
  input.focus();
}

sendBtn.addEventListener("click", handleSend);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") handleSend();
});

init();
