"""Flask backend for the Artisty gallery - LangChain powered smart assistant.

Features:
- Smart gallery assistant with inventory knowledge
- Conversation memory 
- Intent classification
- Pure LLM-based artwork extraction
- Proper country/region filtering
"""

from __future__ import annotations

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from agents import ArtistryAssistant
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    print("[ERROR] Missing OPENAI_API_KEY in backend/.env")
    raise SystemExit(1)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
try:
    with open("art.txt", "r", encoding="utf-8") as f:
        ART_INVENTORY = f.read()
except FileNotFoundError:
    ART_INVENTORY = "Art inventory file not found."

assistant = ArtistryAssistant(ART_INVENTORY, OPENAI_MODEL)

@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "inventory_loaded": ART_INVENTORY != "Art inventory file not found.",
        "assistant_ready": assistant is not None,
    })

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
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

    print(f"\n[USER] {user_message}")
    try:
        result = assistant.process_message(user_message)
        
        print(f"[ASSISTANT] {result.response}")
        print(f"[INTENT] {result.intent}")
        print(f"[ARTWORKS] {result.names}")
        web_actions = []
        if result.names and result.intent in ["art_suggestion", "both"]:
            search_string = " ".join(result.names).lower()
            web_actions = [
                {"type": "search", "value": search_string},
                {"type": "scroll", "value": "art-collection"},
            ]
        
        response_data = {
            "response": result.response,
            "web_actions": web_actions,
            "intent": result.intent,
            "suggested_artworks": result.names,
            "status": "success",
            "agent_used": True,
        }
        
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        response_data = {
            "response": f"I apologize, but I'm having technical difficulties. Please try again! (Error: {str(e)})",
            "web_actions": [],
            "intent": "general_info",
            "suggested_artworks": [],
            "status": "error",
            "agent_used": False,
        }
        
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    print(f"[START] Artisty Backend on http://localhost:{port}")
    print(f"[START] Chat:   http://localhost:{port}/api/chat")
    print(f"[START] Health: http://localhost:{port}/api/health")
    print(f"[START] Assistant initialized with {len(assistant.artwork_names)} artworks")
    app.run(host="localhost", port=port, debug=True)