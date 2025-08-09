# Artisty – AI Gallery Assistant

Artisty is an interactive, **AI agent**-powered art gallery experience. This isn’t just a chatbot that answers questions — it’s a smart, action-oriented assistant that understands what you want and takes steps to deliver it. Think of it like a friendly in-store salesperson who not only recommends the perfect pieces but also physically walks you to them — only here, it’s online, and the AI agent navigates the gallery for you.

<img width="1438" height="763" alt="Screenshot 2025-08-10 at 00 04 41" src="https://github.com/user-attachments/assets/f48d508a-c7fd-4503-b949-039b6b798816" />

<img width="1909" height="909" alt="Screenshot 2025-08-09 at 23 46 37" src="https://github.com/user-attachments/assets/a0db07cf-a17b-4403-9ba5-2385f73bb64f" />

<img width="1293" height="964" alt="image" src="https://github.com/user-attachments/assets/8cc4ad75-ae1c-44c3-b1e2-4ab472bba020" />

---

## Overview

Artisty blends a modern **React/Vite frontend** with a **Python/Flask backend** powered by OpenAI’s Responses API. The AI agent understands natural language queries about style, theme, origin, price, or even abstract concepts, and then:

1. **Finds the right artworks** from your curated inventory.
2. **Takes action** by focusing the on-screen gallery on those pieces.

The result is a dynamic, fun, and friendly browsing experience — more like interacting with a knowledgeable guide than just typing into a search box.

---

## Current Features

* **AI Agent-driven discovery**
  Ask for art by country, region, style, theme, color, price, or a specific title (e.g., “naturalistic blend of animal and bird”), and the AI agent will both answer and act.

* **Two-pass LLM flow with fallback**

  1. **Pass 1**: AI agent generates a short, friendly reply suggesting 2–5 works from the actual inventory.
  2. **Pass 2**: Extracts the titles for gallery navigation.
  3. **Fallback**: If extraction misses titles, the backend deterministically matches them from the reply.

* **Action-oriented navigation**
  The AI agent not only recommends but also scrolls or focuses the gallery so the suggested pieces are front and center.

* **Inventory-grounded results**
  The AI agent only uses artworks from `backend/art.txt`, with geographic mappings for broader queries.

* **Clean and modular architecture**

  * React/Vite UI with a docked chat widget.
  * Flask backend with minimal endpoints for health and chat.

---
## Live Demo
- **Frontend:** [https://main.d1lzbp0aw93yrh.amplifyapp.com/](https://main.d1lzbp0aw93yrh.amplifyapp.com/)
- **Portfolio:** [https://kailash.london/](https://kailash.london/)  
- **Hackathon Submission Presentation:** [PPTX Link](https://docs.google.com/presentation/d/1jJuar2xDy54ieuVl4fe6pKGMCWLgdfOtoMt2JLQufm4/edit?usp=sharing)  

## Architecture

**Frontend (`artisty-frontend/`)**

* React + Vite
* Chat UI component (`ChatBot.jsx`) to send queries and trigger gallery actions
* State management for search/focus

**Backend (`backend/`)**

* Flask app (`app.py`)
* Inventory in `art.txt`
* Prompts in `prompts.py` for AI agent’s Pass 1 & 2 logic
* Deterministic title-matching fallback

**Data Flow**

1. User sends query → AI agent runs Pass 1 → returns friendly suggestions
2. Backend extracts titles → frontend triggers gallery focus
3. If LLM fails extraction, fallback ensures titles are still matched

---

## Setup

**Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Environment Variables (`.env`)**

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini-2024-07-18
PORT=5050
```

**Run Backend**

```bash
python app.py
```

**Frontend**

```bash
cd artisty-frontend
npm install
npm run dev
```

Visit: [http://localhost:5173](http://localhost:5173)

---

## Future Scope

* **Blockchain integration** for provenance and authenticity:

  * Smart contracts for transparent transactions without middlemen.
  * On-chain ownership history and anti-duplication safeguards.
  * Tokenized authenticity certificates (NFT or verifiable credentials).
  * Automated percentage splits to designated wallets.

* **Multi-agent orchestration**

  * Planner agent to decide on filters, comparisons, and upselling.
  * Critic agent to validate suggestions against style/geography rules.

* **Personalization**

  * Session-based memory for preferences (colors, price range, origins).
  * Progressive recommendations over time.

* **Traceability**

  * IPFS or similar content-addressed storage for artwork metadata.
  * Public verification pages for provenance.

---

## License

MIT

---

## Acknowledgements

* Built with React, Vite, Flask, and OpenAI’s Responses API.
* Inventory
