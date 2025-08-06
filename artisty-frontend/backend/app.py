import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 DEBUG: Starting Artisty Backend...")
print(f"🔧 DEBUG: OPENAI_API_KEY loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

# Import OpenAI
try:
    from openai import OpenAI
    print("🔧 DEBUG: OpenAI library imported successfully")
except ImportError:
    print("❌ ERROR: OpenAI package not found. Install with: pip install openai")
    raise

app = Flask(__name__)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
print(f"🔧 DEBUG: OpenAI API key configured: {'Yes' if api_key else 'No'}")

if api_key:
    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized successfully")
else:
    print("❌ Failed to get OpenAI API key")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
print(f"🔧 DEBUG: OPENAI_MODEL configured: {OPENAI_MODEL}")

# Simple system prompt for art assistant
SYSTEM_PROMPT = "You are an AI assistant for Artisty, a premium art marketplace. Help customers with art discovery, artist information, and purchase guidance. Be knowledgeable about art history."

@app.route('/health', methods=['GET'])
def health():
    print("🔧 DEBUG: Health check requested")
    return jsonify({"status": "healthy"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    print("🔧 DEBUG: Chat request received")
    
    # Handle CORS preflight OPTIONS request
    if request.method == 'OPTIONS':
        print("🔧 DEBUG: Handling OPTIONS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            print("❌ DEBUG: No JSON data in request")
            return jsonify({"error": "No data provided"}), 400
        
        user_message = data.get("message")
        if not user_message:
            print("❌ DEBUG: No message in request")
            return jsonify({"error": "No message provided"}), 400
        
        print(f"🔧 DEBUG: User message: {user_message[:50]}...")
        
        # Prepare OpenAI request
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        print("🔧 DEBUG: Calling OpenAI API...")
        
        # Call OpenAI using new client format (matching lambda function)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=int(os.getenv("MAX_TOKENS", "300")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
        
        bot_response = response.choices[0].message.content
        print(f"🔧 DEBUG: OpenAI response: {bot_response[:50]}...")
        
        response = jsonify({
            "response": bot_response,
            "status": "success"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as openai_error:
        error_message = str(openai_error)
        if "authentication" in error_message.lower():
            print("❌ DEBUG: OpenAI authentication failed")
            return jsonify({"error": "Invalid API key"}), 401
        elif "rate limit" in error_message.lower():
            print("❌ DEBUG: OpenAI rate limit exceeded")
            return jsonify({"error": "Rate limit exceeded"}), 429
        else:
            print(f"❌ DEBUG: OpenAI API error: {error_message}")
            return jsonify({"error": f"OpenAI API error: {error_message}"}), 500
    except Exception as e:
        print(f"❌ DEBUG: Error in chat: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in .env file!")
        exit(1)
    
    port = int(os.getenv("PORT", "5000"))
    print(f"🚀 DEBUG: Starting server on port {port}")
    print(f"🔗 DEBUG: API available at: http://localhost:{port}/api/chat")
    
    app.run(host='localhost', port=port, debug=True)