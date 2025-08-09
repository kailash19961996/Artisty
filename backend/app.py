"""Flask backend for the Artisty gallery chatbot and API.

Two-pass flow using OpenAI Responses API:
- Pass 1: Send the user's message + inventory; get a short witty reply with 3–5 suggestions.
- Pass 2: Send the first-pass reply; extract only artwork names as a space-separated list
          (two words per artwork). Use the first name to trigger a frontend search.
"""

from __future__ import annotations

import os
from flask import Flask, request, jsonify
import re
from flask_cors import CORS
from dotenv import load_dotenv
from prompts import (
    build_first_pass_user_prompt,
    build_second_pass_user_prompt,
)

# ----------------------------------------------------------------------------
# Env & OpenAI client
# ----------------------------------------------------------------------------
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] Install OpenAI SDK: pip install openai==1.*")
    raise

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_MODEL1 = os.getenv("OPENAI_MODEL1")

if not OPENAI_API_KEY or not OPENAI_MODEL:
    print("[ERROR] Missing OPENAI_API_KEY or OPENAI_MODEL in backend/.env")
    raise SystemExit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------------------------------------------
# App setup
# ----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# Load inventory once
try:
    with open("art.txt", "r", encoding="utf-8") as f:
        ART_INVENTORY = f.read()
except FileNotFoundError:
    ART_INVENTORY = "Art inventory file not found."

# ----------------------------------------------------------------------------
# Deterministic extraction helpers
# ----------------------------------------------------------------------------
def _get_inventory_art_names(inventory_text: str) -> list[str]:
    names: list[str] = []
    for line in inventory_text.splitlines():
        line = line.strip()
        if ". " in line and " - " in line:
            left = line.split(" - ")[0]
            if ". " in left:
                name = left.split(". ", 1)[1].strip()
                if name:
                    names.append(name)
    return names

_INVENTORY_NAMES_LOWER = [n.lower() for n in _get_inventory_art_names(ART_INVENTORY)]

# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "inventory_loaded": ART_INVENTORY != "Art inventory file not found.",
    })

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    # CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # ----- Pass 1: witty reply + 3–5 suggestions from inventory -----
    inventory_block = f"INVENTORY:\n{ART_INVENTORY}"
    first_pass_input = f"{inventory_block}\n\n{build_first_pass_user_prompt(user_message)}"
    try:
        r1 = client.responses.create(model=OPENAI_MODEL, input=first_pass_input)
        bot_response = (r1.output_text or "").strip()
    except Exception as e:
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500

    print(f"user_message: {user_message}")
    print(f"bot_response: {bot_response}")

    # ----- Pass 2: extract artwork names from pass-1 output -----
    # Try deterministic match against known inventory names
    text_lower = bot_response.lower()
    names = [n for n in _INVENTORY_NAMES_LOWER if n in text_lower]
    print("[PASS2-det]", names)

    # Fallback to LLM extractor if none matched
    if not names:
        second_pass_input = build_second_pass_user_prompt(bot_response)
        try:
            r2 = client.responses.create(model=OPENAI_MODEL1 or OPENAI_MODEL, input=second_pass_input)
            raw_names = (r2.output_text or "").strip().lower()
        except Exception:
            raw_names = ""
        print("[PASS2-llm]", raw_names)
        tokens = [re.sub(r"[^a-z0-9]", "", t) for t in raw_names.split()]
        tokens = [t for t in tokens if t]
        names = [" ".join(tokens[i:i+2]) for i in range(0, len(tokens), 2) if i + 1 < len(tokens)]

    # Convert to a single space-separated string of names
    names_string = " ".join(names)
    print(f"names_string: {names_string}")

    web_actions = []
    if names_string:
        web_actions = [
            {"type": "search", "value": names_string},
            {"type": "scroll", "value": "art-collection"},
        ]

    print(f"web_actions: {web_actions}")

    response = jsonify({
        "response": bot_response,
        "web_actions": web_actions,
        "art_suggestions": [],
        "status": "success",
        "agent_used": False,
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# ----------------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    print(f"[START] Artisty Backend on http://localhost:{port}")
    print(f"[START] Chat:   http://localhost:{port}/api/chat")
    print(f"[START] Health: http://localhost:{port}/api/health")
    app.run(host="localhost", port=port, debug=True)
