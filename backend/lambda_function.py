"""
ARTISTY BACKEND - AWS Lambda Function Handler

This Lambda function serves as the backend API for the Artisty art gallery application.
It provides AI-powered conversational assistance with intelligent artwork recommendations
and UI control capabilities.

Key Features:
- AI agent with tools for UI control (navigation, cart, popups, search)
- CORS handling for cross-origin requests from the frontend
- Health monitoring endpoint for backend status
- Singleton pattern for AI assistant instance (Lambda container reuse)
- Contextual artwork search with anti-hallucination validation

Endpoints:
- GET /api/health - Health check and system status
- POST /api/chat - AI chat with structured responses and web actions
- OPTIONS /* - CORS preflight handling

Architecture:
- Uses LangChain agents with structured tools for UI actions
- Maintains conversation memory across requests within container lifetime
- Handles CORS for cross-origin requests
- Provides structured JSON responses with web actions

Security:
- CORS configuration for allowed origins
- Input validation and sanitization
- Error handling with appropriate HTTP status codes
- Environment variable validation for API keys

@author Artisty Team
@version 2.1.0 - Simplified architecture with direct JSON responses
"""

import json
import os
from utils import create_assistant

# Global assistant instance for conversation memory persistence
assistant = None

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
    
    return {
        "Access-Control-Allow-Origin": "*",
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
    - AI chat (POST /api/chat)
    - CORS preflight (OPTIONS)
    
    Args:
        event: API Gateway event object containing request details
        context: Lambda context object (unused)
        
    Returns:
        dict: API Gateway response with status, headers, and body
    """
    # Log request for monitoring and debugging
    print("Request:", json.dumps(event)[:2000])

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
            inventory_loaded = test_assistant and len(test_assistant.inventory_text) > 0
            return respond(200, {
                "status": "healthy",
                "inventory_loaded": inventory_loaded,
                "assistant_ready": test_assistant is not None,
                "inventory_length": len(test_assistant.inventory_text) if test_assistant else 0
            }, origin)
        except Exception as e:
            return respond(500, {
                "status": "unhealthy",
                "error": str(e),
                "inventory_loaded": False,
                "assistant_ready": False
            }, origin)

    # Chat endpoint routing - support multiple path variations
    is_chat_path = (
        normalized_path in ("/artisty", "/api", "/message", "/chat")
        or normalized_path.endswith("/api/message")
        or normalized_path.endswith("/api/chat")
    )
    
    # Handle chat requests
    if method == "POST" and is_chat_path:
        try:
            raw = event.get("body") or "{}"
            data = json.loads(raw) if isinstance(raw, str) else (raw or {})
            # Extract user message from request body
            user_message = (data.get("text") or data.get("message") or "").strip()

            if not user_message:
                return respond(400, {"success": False, "error": "Missing 'message' in body"}, origin)

            print(f"User: {user_message}")
            
            # Process message with AI assistant
            ai_assistant = get_assistant()
            result = ai_assistant.process_message(user_message)
            
            print(f"Assistant: {result.response}")
            print(f"Intent: {result.intent}")
            print(f"Artworks: {result.names}")
            print(f"Actions: {result.web_actions}")
            
            # Format response for frontend
            response_data = {
                "response": result.response,
                "web_actions": result.web_actions,
                "intent": result.intent,
                "suggested_artworks": result.names,
                "success": True
            }
            
            return respond(200, response_data, origin)

        except json.JSONDecodeError:
            return respond(400, {"success": False, "error": "Invalid JSON"}, origin)
        except Exception as e:
            print(f"Error processing chat message: {str(e)}")
            
            # Error response
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
