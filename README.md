# ⚡ Kalki Core – Free, Browser‑Native AI Platform

This single repository contains the entire Kalki platform:
- **Chat UI** (index.html) – Unlimited AI tokens via WebLLM.
- **Worker UI** (worker.html) – Earn points by sharing idle GPU.
- **Orchestrator** (GitHub Actions) – Distributes tasks, verifies work, and manages points.

**Zero cost, zero servers, zero credit card.** Runs entirely on GitHub Pages and GitHub Actions.

## Quick Start
1. Fork/clone this repo.
2. In repo settings → **Pages**, set source to `main` branch and folder `/ (root)`.
3. Enable **GitHub Issues** (Settings → General → Issues).
4. Update `OWNER` and `REPO` in `assets/worker.js` (line 4 & 5) to match your GitHub username and repo name.
5. Push to GitHub. The site will be live at `https://<your-username>.github.io/kalkicore/`.

## Configuration
- The orchestrator runs every 5 minutes automatically (`.github/workflows/orchestrator.yml`).
- Edit `tasks.json` to add or remove pending compute tasks.
- Model is loaded from MLC’s CDN; no model files need to be stored here.

## License
AGPL-3.0
