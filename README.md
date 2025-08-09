# Artisty – AI Gallery Assistant

A modern web experience that helps people discover artwork using a conversational AI assistant. It blends a beautiful React/Vite frontend with a lightweight Python/Flask backend powered by OpenAI’s Responses API. The system understands natural language (country, style, theme, color, price, names) and shows relevant pieces from a curated inventory.

This README is written for both non‑technical and technical readers. Skim the Overview and Features if you want the big picture; jump to Architecture and Development if you’re building.

---

## Overview (for everyone)

- The site showcases a curated gallery of 60+ artworks with names, prices, countries, and short descriptions.
- A friendly assistant named “Purple” chats with you about what you like and suggests art to match.
- It uses a “two‑pass” approach:
  1) The AI replies in a short, funny tone and lists 2–5 relevant artworks from the gallery.
  2) It then extracts the mentioned artwork names and triggers a search so you see them on screen.
- If the AI misses a name, the backend has a deterministic fallback that scans the reply and finds inventory names directly.
- Everything runs locally: React/Vite frontend, Flask backend.

What you can do now:
- Ask for art by country/region (e.g., “from Africa”, “from UK”), style, theme, color, price range, or specific title.
- Get a compact set of suggestions with short descriptions and see the results populate in the gallery.

---

## Key Features

- Conversational discovery with a two‑pass LLM flow (Responses API)
  - Pass 1: Understands your request and proposes 2–5 pieces from the actual inventory (`backend/art.txt`).
  - Pass 2: Extracts the artwork names from the reply and triggers a gallery search.
  - Deterministic fallback: If the LLM doesn’t extract names, the backend matches known names in the reply text.
- Strict, inventory‑grounded suggestions
  - Country/region mappings (e.g., “South America → Brazil, Argentina”) ensure relevant origin filters.
  - Uses only real names from the gallery; avoids hallucinated titles.
- Clean, simple backend
  - Flask + CORS, `.env` driven config, print‑only logs.
  - Uses OpenAI Responses API (no chat/completions legacy params).
- Smooth frontend
  - React (Vite) UI with a modern layout and a docked chat widget.
  - Vite proxy routes `/api/*` to the local backend for easy local dev.

---

## Architecture (for builders)

- Frontend: `artisty-frontend/`
  - React + Vite
  - Chat UI component (`src/components/ChatBot.jsx`)
  - Calls `/api/chat` (proxied to the backend) and dispatches search events
- Backend: `backend/`
  - Flask (`app.py`) with two endpoints:
    - `GET /api/health` – simple health check
    - `POST /api/chat` – two‑pass flow
  - Inventory in `backend/art.txt`
  - Prompts in `backend/prompts.py` (short, focused)
- Two‑pass flow
  - Pass 1 input = inventory + “first‑pass” prompt + user message
  - Pass 1 output = friendly text with 2–5 recommendations (names + brief phrases)
  - Pass 2 = extract names; deterministic fallback scans reply for any inventory titles
  - Frontend then searches and scrolls to the gallery

---

## Setup (local development)

Prereqs
- Python 3.9+
- Node.js 18+ (recommend 20 via nvm) and npm

Backend
1) Create a venv and install deps:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
2) Create `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini-2024-07-18   # or your chosen model
   # Optional: a different model for pass 2 extraction
   OPENAI_MODEL1=
   PORT=5050
   ```
3) Run the backend:
   ```bash
   python app.py
   ```
   - Health: `http://localhost:5050/api/health`
   - Chat: `http://localhost:5050/api/chat`

Frontend
1) Install and run:
   ```bash
   cd artisty-frontend
   npm install
   npm run dev
   ```
2) Open `http://localhost:5173`
   - Vite proxy sends `/api/*` to `http://localhost:5050`.

Troubleshooting
- Port 5000 may be used by macOS AirPlay; this project uses port 5050 to avoid conflicts.
- If npm is “not found,” load nvm (or install Node with Homebrew or nodejs.org).
- If the AI returns parameter errors, ensure the backend uses `Responses API` and your model supports the used options.
- If chat suggestions appear but the gallery doesn’t update, check DevTools → Network for `/api/chat` and confirm `200`.

---

## Configuration

Environment variables (backend/.env):
- `OPENAI_API_KEY` – your OpenAI key
- `OPENAI_MODEL` – model name for pass 1 (e.g., `gpt-4o-mini-2024-07-18`)
- `OPENAI_MODEL1` – optional model for pass 2 extraction (falls back to `OPENAI_MODEL` if unset)
- `PORT` – backend port (default 5050)

Frontend (optional):
- `artisty-frontend/.env.local` with `VITE_API_BASE_URL=http://localhost:5050` (Vite proxy already covers `/api/*`).

---

## Current AI “Agentic” Capacity

- Goal‑driven response shaping: The “first pass” prompt instructs the model to understand the core user intent (country/region/continent, style, theme, color, price, or specific name) and produce only inventory‑backed suggestions.
- Tool‑like behavior without external tools: The “second pass” behaves like a simple extraction tool. If it fails, the backend’s deterministic extractor substitutes, keeping the system reliable.
- Grounded answers: All suggestions are drawn from `art.txt`. The system discourages hallucinated titles.

Limitations to be aware of
- LLMs can still misinterpret nuanced geography or styles; we mitigate via explicit mapping rules and inventory‑only constraints.
- Extraction can fail under ambiguous phrasing; the deterministic fallback minimizes UX impact.

---

## Future Scope: Deeper AI Agents & Traceable Commerce

- Multi‑agent orchestration
  - Planner/Router agent to decide which capabilities to use (search, filter, compare, summarize, price justify, upsell, etc.)
  - Critic/Refiner agent to check geographic/style consistency and correct mismatches before sending suggestions
- Personalization & memory
  - Lightweight preference memory (liked countries, colors, budgets) with transparent controls and opt‑out
  - Session scoring and progressive recommendations
- Retrieval‑augmented generation (RAG)
  - Vector search over extended catalogs and artist bios
  - Private, curated sources for higher precision
- Observability & safety
  - Traces for every decision (input, prompt, model, output, user actions)
  - Guardrails for tone, safe content, and bias checks
- Smart‑contract integration for trust and provenance
  - On‑chain registries for artwork provenance and ownership history
  - Tokenized certificates of authenticity (NFT or soul‑bound credentials)
  - Escrow or milestone smart contracts for purchases and commissions
  - Wallet‑based checkout (Sign‑in with Ethereum, Solana, or other chains)
- Traceability features
  - Content‑addressed storage (e.g., IPFS) for images + metadata
  - Cryptographic hashes written on‑chain for immutable provenance
  - Attestations (EAS/Verifiable Credentials) to link artist → gallery → buyer
  - Public verification page that proves authenticity and chain of custody

---

## How It Works (deeper dive)

1) User sends a message via chat
2) Backend builds input for Pass 1: inventory + focused “first‑pass” prompt + user message
3) Pass 1 model returns a friendly reply with 2–5 real titles
4) Backend extracts titles for Pass 2
   - Deterministic: scan reply for exact inventory names (first choice)
   - LLM fallback: prompt the model to output only names as a single space‑separated string
5) Frontend receives the reply + search actions and updates the gallery

---

## Contributing

- Keep prompts short and directive; prefer constraints over examples.
- Favor deterministic fallbacks when extraction is failure‑prone.
- Match existing code style and keep edits minimal and focused.

---

## License

MIT (replace if your organization needs a different license).

---

## Acknowledgements

- Built with React, Vite, Flask, and OpenAI’s Responses API.
- Inventory is synthetic for demo purposes; replace `backend/art.txt` with your catalog.
