# ⚡ KalkiCore – Universal, Tiny‑Model AI Chat

A completely free, browser‑native AI chat that works on **any** WebGPU‑capable device, including Intel UHD Graphics 620 and integrated GPUs.  
It uses the **tiny Qwen2.5‑0.5B** model (<1 GB) to guarantee broad compatibility and instant loading.

**No server, no API keys, unlimited tokens.**

## Features
- 🔍 Dynamic hardware detection – shows your GPU and estimated memory
- 📋 Full logging in the UI and JavaScript console
- 🔗 Live integration with the Kalki Worker mesh (points, pending tasks)
- ⚡ One‑click deploy via GitHub Pages

## Setup
1. Fork / clone this repository.
2. Enable GitHub Pages in Settings → Pages (source: `main` branch, `/` root).
3. (Optional) Set up a GitHub personal access token with `public_repo` scope as a repository secret named `GITHUB_TOKEN` to enable the orchestrator.
4. Visit `https://<your-username>.github.io/kalkicore/` and start chatting!

## Why only one tiny model?
We prioritise universal access over raw power. The Qwen2.5‑0.5B model runs on almost any device with WebGPU, and we intend to support model‑of‑choice via the worker mesh in future releases.
