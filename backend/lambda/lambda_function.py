import json
import os
from utils import create_assistant

# Initialize the assistant globally for Lambda reuse
assistant = None

ALLOWED_ORIGINS = [
    # Production Amplify app (no trailing slash; CORS requires exact match)
    "https://main.d22zce484yggk5.amplifyapp.com",
    "https://main.d22zce484yggk5.amplifyapp.com/",
    # Common local dev origins
    "http://localhost:5173",
    "http://localhost:5173/",
    "https://localhost:5173/",
    "http://localhost:5050",
    "http://localhost:3000",
    "http://127.0.0.1:5173"
]

ALLOWED_METHODS = "GET,POST,OPTIONS"
ALLOWED_HEADERS = "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token"

def cors_headers(origin: str | None) -> dict:
    allowed_origin = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    return {
        "Access-Control-Allow-Origin": *,
        "Access-Control-Allow-Credentials": "false",
        "Access-Control-Allow-Methods": ALLOWED_METHODS,
        "Access-Control-Allow-Headers": ALLOWED_HEADERS,
        "Access-Control-Max-Age": "7200",
        "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
        "Content-Type": "application/json",
    }

def respond(status: int, body: dict, origin: str | None) -> dict:
    return {
        "statusCode": status,
        "headers": cors_headers(origin),  # Always use the same CORS headers
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }

def get_assistant():
    """Get or create the assistant instance (singleton for Lambda container reuse)"""
    global assistant
    if assistant is None:
        try:
            # Get OpenAI API key from environment
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise Exception("OPENAI_API_KEY environment variable not set")
            
            assistant = create_assistant(openai_api_key=openai_api_key)
            print("Assistant initialized successfully")
        except Exception as e:
            print(f"Error initializing assistant: {str(e)}")
            raise
    return assistant


def lambda_handler(event, context):
    # Basic logging to CloudWatch
    print("Event:", json.dumps(event)[:2000])

    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin")
    method = event.get("httpMethod", "")
    path = event.get("path", "") or ""
    # Normalize path for matching regardless of stage name or trailing slashes
    normalized_path = path.split("?")[0].rstrip("/") or "/"
    if normalized_path.startswith("/default"):
        normalized_path = normalized_path[len("/default"): ] or "/"

    # Preflight
    if method == "OPTIONS":
        return respond(200, {"message": "CORS preflight ok"}, origin)

    # Health check
    if method == "GET" and (normalized_path.endswith("/health") or normalized_path == "/health"):
        try:
            # Check if assistant can be initialized
            test_assistant = get_assistant()
            inventory_loaded = test_assistant and len(test_assistant.artwork_names) > 0
            return respond(200, {
                "status": "healthy",
                "inventory_loaded": inventory_loaded,
                "assistant_ready": test_assistant is not None,
                "artwork_count": len(test_assistant.artwork_names) if test_assistant else 0
            }, origin)
        except Exception as e:
            return respond(500, {
                "status": "unhealthy",
                "error": str(e),
                "inventory_loaded": False,
                "assistant_ready": False
            }, origin)

    # Chat/message endpoint – accept several common paths
    is_chat_path = (
        normalized_path in ("/artisty", "/api", "/message", "/chat")
        or normalized_path.endswith("/api/message")
        or normalized_path.endswith("/api/chat")
    )
    if method == "POST" and is_chat_path:
        try:
            raw = event.get("body") or "{}"
            data = json.loads(raw) if isinstance(raw, str) else (raw or {})
            # Support either 'text' or 'message' fields from the frontend
            user_message = (data.get("text") or data.get("message") or "").strip()

            if not user_message:
                return respond(400, {"success": False, "error": "Missing 'message' in body"}, origin)

            print(f"\n[USER] {user_message}")
            
            # Get the assistant and process the message
            ai_assistant = get_assistant()
            result = ai_assistant.process_message(user_message)
            
            print(f"[ASSISTANT] {result.response}")
            print(f"[INTENT] {result.intent}")
            print(f"[ARTWORKS] {result.names}")
            
            # Handle web actions from the agent
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
                "success": True,
            }
            
            return respond(200, response_data, origin)

        except json.JSONDecodeError:
            return respond(400, {"success": False, "error": "Invalid JSON"}, origin)
        except Exception as e:
            print(f"Error processing chat message: {str(e)}")
            
            # Fallback response
            response_data = {
                "response": f"I apologize, but I'm having technical difficulties. Please try again! (Error: {str(e)})",
                "web_actions": [],
                "intent": "general_info",
                "suggested_artworks": [],
                "status": "error",
                "agent_used": False,
                "success": False,
                "error": str(e)
            }
            
            return respond(500, response_data, origin)

    # Fallback
    return respond(405, {"success": False, "error": "Method or path not allowed"}, origin)
