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
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import time
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
    return _chat_handler(stream=False)

@app.route("/api/chat/stream", methods=["POST", "OPTIONS"])
def chat_stream():
    return _chat_handler(stream=True)

def _chat_handler(stream=False):
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        # Explicitly allow both POST and OPTIONS for CORS preflight
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400

    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    print(f"\n[USER] {user_message}")
    
    if stream:
        def generate_stream():
            try:
                for chunk_data in assistant.process_message_stream(user_message):
                    # Add CORS headers to each chunk
                    chunk_json = json.dumps(chunk_data)
                    yield f"data: {chunk_json}\n\n"
                    time.sleep(0.05)  # Small delay for smoother streaming
                    
                    if chunk_data.get("is_complete"):
                        print(f"[ASSISTANT] {chunk_data.get('full_response', '')}")
                        print(f"[INTENT] {chunk_data.get('intent', '')}")
                        print(f"[ARTWORKS] {chunk_data.get('suggested_artworks', [])}")
                        print(f"[DEBUG] Web actions: {chunk_data.get('web_actions', [])}")
                        
            except Exception as e:
                print(f"[ERROR] {str(e)}")
                error_data = {
                    "chunk": f"I apologize, but I'm having technical difficulties. Please try again! (Error: {str(e)})",
                    "is_complete": True,
                    "web_actions": [],
                    "intent": "general_info",
                    "suggested_artworks": [],
                    "full_response": f"Error: {str(e)}"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        response = Response(generate_stream(), mimetype='text/plain')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Cache-Control", "no-cache")
        response.headers.add("Connection", "keep-alive")
        return response
    
    else:
        # Non-streaming response (existing logic)
        try:
            result = assistant.process_message(user_message)

            print(f"[ASSISTANT] {result.response}")
            print(f"[INTENT] {result.intent}")
            print(f"[ARTWORKS] {result.names}")
            # Use web actions from agent result
            web_actions = result.web_actions if hasattr(result, 'web_actions') else []
            print(f"[DEBUG] Web actions being sent to frontend: {web_actions}")

            # include both keys for compatibility: 'web_actions' and short alias 'actions'
            response_data = {
                "response": result.response,
                "web_actions": web_actions,
                "actions": web_actions,
                "intent": result.intent,
                "suggested_artworks": result.names,
                "status": "success",
                "agent_used": True,
            }
            print(f"[DEBUG] Full response data: {response_data}")

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


# Provide a non-prefixed alias to match callers that hit `/chat`
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat_no_api():
    return chat()
        
if __name__ == "__main__":
    port = 5000  # Use the standard Flask dev port to match default behavior
    print(f"[START] Artisty Backend on http://127.0.0.1:{port}")
    print(f"[START] Chat:   http://127.0.0.1:{port}/api/chat")
    print(f"[START] Health: http://127.0.0.1:{port}/api/health")
    print(f"[START] Assistant initialized with {len(assistant.artwork_names)} artworks")
    app.run(host="127.0.0.1", port=port, debug=True)