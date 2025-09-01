"""
ARTISTY BACKEND - AWS Lambda Function Handler

This Lambda function serves as the backend API for the Artisty art gallery application.
It provides AI-powered conversational assistance with real-time streaming responses
and agentic UI control capabilities.

Key Features:
- Server-Sent Events (SSE) streaming for real-time word-by-word responses
- AI agent with tools for UI control (navigation, cart, popups, search)
- CORS handling for cross-origin requests from the frontend
- Health monitoring endpoint for backend status
- Singleton pattern for AI assistant instance (Lambda container reuse)

Endpoints:
- GET /api/health - Health check and system status
- POST /api/chat/stream - Streaming AI chat with real-time actions
- POST /api/chat - Non-streaming AI chat (fallback)
- OPTIONS /* - CORS preflight handling

Architecture:
- Uses LangChain agents with structured tools for UI actions
- Implements streaming response generation with SSE format
- Maintains conversation memory across requests within container lifetime
- Handles CORS for multiple allowed origins (dev, production)

Security:
- CORS whitelist for allowed origins
- Input validation and sanitization
- Error handling with appropriate HTTP status codes
- Environment variable validation for API keys

@author Artisty Team
@version 2.0.0 - Added SSE streaming and agentic capabilities
"""

import json
import os
from utils import create_assistant

# Initialize the assistant globally for Lambda container reuse
# This enables conversation memory persistence across requests
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
    """
    Generate CORS headers for API responses
    
    Handles cross-origin requests by setting appropriate CORS headers.
    Uses whitelist approach for security - only allows specific origins.
    
    Args:
        origin: The origin header from the request
        
    Returns:
        dict: CORS headers for the response
    """
    allowed_origin = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    return {
        "Access-Control-Allow-Origin": allowed_origin,
        "Access-Control-Allow-Credentials": "false",
        "Access-Control-Allow-Methods": ALLOWED_METHODS,
        "Access-Control-Allow-Headers": ALLOWED_HEADERS,
        "Access-Control-Max-Age": "7200",
        "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
        "Content-Type": "application/json",
    }

def respond(status: int, body: dict, origin: str | None) -> dict:
    """
    Create a standardized API Gateway response with CORS headers
    
    Args:
        status: HTTP status code
        body: Response body as dictionary
        origin: Request origin for CORS headers
        
    Returns:
        dict: API Gateway-formatted response
    """
    return {
        "statusCode": status,
        "headers": cors_headers(origin),
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }

def get_assistant():
    """
    Get or create the AI assistant instance (singleton pattern)
    
    Uses global variable to maintain assistant instance across Lambda invocations
    within the same container, enabling conversation memory persistence.
    
    Returns:
        ArtistryAssistant: The AI assistant instance
        
    Raises:
        Exception: If OpenAI API key is not configured or assistant initialization fails
    """
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
    """
    AWS Lambda entry point for the Artisty backend API
    
    Handles all HTTP requests from the frontend, routing them to appropriate
    handlers based on the HTTP method and path. Supports:
    - Health checks (GET /api/health)
    - AI chat streaming (POST /api/chat/stream) 
    - AI chat non-streaming (POST /api/chat)
    - CORS preflight (OPTIONS)
    
    Args:
        event: API Gateway event object containing request details
        context: Lambda context object (unused)
        
    Returns:
        dict: API Gateway response with status, headers, and body
    """
    # Basic logging to CloudWatch for debugging
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
    
    # Streaming chat endpoint
    is_stream_path = (
        normalized_path.endswith("/api/chat/stream")
        or normalized_path.endswith("/chat/stream")
    )
    
    # Handle streaming chat endpoint
    if method == "POST" and is_stream_path:
        try:
            raw = event.get("body") or "{}"
            data = json.loads(raw) if isinstance(raw, str) else (raw or {})
            user_message = (data.get("text") or data.get("message") or "").strip()

            if not user_message:
                return respond(400, {"success": False, "error": "Missing 'message' in body"}, origin)

            print(f"\n[USER] {user_message}")
            print(f"[DEBUG] Processing streaming request for path: {normalized_path}")
            
            # Get the assistant and process the message with streaming
            ai_assistant = get_assistant()
            
            # Build SSE response
            sse_chunks = []
            
            for chunk_data in ai_assistant.process_message_stream(user_message):
                # Convert each chunk to SSE format
                sse_line = f"data: {json.dumps(chunk_data)}\n\n"
                sse_chunks.append(sse_line)
                print(f"[DEBUG] Generated SSE chunk: {len(sse_line)} bytes")
                
                if chunk_data.get("is_complete"):
                    print(f"[ASSISTANT] {chunk_data.get('full_response', '')}")
                    print(f"[INTENT] {chunk_data.get('intent', '')}")
                    print(f"[ARTWORKS] {chunk_data.get('suggested_artworks', [])}")
                    print(f"[DEBUG] Web actions: {chunk_data.get('web_actions', [])}")
                    break
            
            print(f"[DEBUG] Total SSE chunks: {len(sse_chunks)}, Total response size: {len(''.join(sse_chunks))} bytes")
            
            # Return SSE response with custom headers (don't use cors_headers which sets JSON content-type)
            cors_base = cors_headers(origin)
            sse_headers = {
                **cors_base,
                "Content-Type": "text/plain; charset=utf-8",  # Override JSON content-type for SSE
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
            
            return {
                "statusCode": 200,
                "headers": sse_headers,
                "body": "".join(sse_chunks),  # All SSE chunks as one string
                "isBase64Encoded": False,
            }
            
        except json.JSONDecodeError:
            return respond(400, {"success": False, "error": "Invalid JSON"}, origin)
        except Exception as e:
            print(f"Error processing streaming chat message: {str(e)}")
            return respond(500, {"success": False, "error": str(e)}, origin)
    
    # Handle regular chat endpoint
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
            
            # Use web actions from agent result (matches main.py functionality)
            web_actions = result.web_actions if hasattr(result, 'web_actions') else []
            print(f"[DEBUG] Web actions being sent to frontend: {web_actions}")
            
            # Include both keys for compatibility: 'web_actions' and short alias 'actions'
            response_data = {
                "response": result.response,
                "web_actions": web_actions,
                "actions": web_actions,  # Compatibility alias
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
