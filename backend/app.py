"""Flask backend for the Artisty gallery chatbot and API.

This service exposes chat endpoints, loads inventory from `art.txt`, and
integrates with OpenAI to produce conversational and search-triggered
responses for the frontend.
"""

import json
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from prompts import (
    build_shopkeeper_system_prompt,
    build_first_pass_user_prompt,
    build_keyword_selector_system_prompt,
)

# Load environment variables
load_dotenv()

# Setup simple logging without emojis
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(stream_handler)
logger = logging.getLogger('ArtistyBackend')

# Chat logger uses the same stream handler; avoid writing to log files
chat_logger = logging.getLogger('ChatbotInteractions')
chat_logger.handlers = []
chat_logger.propagate = True
chat_logger.setLevel(logging.INFO)

logger.info("[INIT] Starting Artisty Backend...")
logger.info(f"[INIT] OPENAI_API_KEY loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

# Import OpenAI (skip LangChain for now)
try:
    from openai import OpenAI
    logger.info("[SUCCESS] OpenAI library imported successfully")
except ImportError as e:
    logger.error(f"[ERROR] OpenAI import failed: {e}")
    exit(1)

app = Flask(__name__)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"[CONFIG] OpenAI API key configured: {'Yes' if api_key else 'No'}")

if api_key:
    client = OpenAI(api_key=api_key)
    logger.info("[SUCCESS] OpenAI client initialized successfully")
else:
    logger.error("[ERROR] Failed to get OpenAI API key")
    exit(1)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
logger.info(f"[CONFIG] OPENAI_MODEL configured: {OPENAI_MODEL}")

def get_valid_search_keywords_from_inventory(inventory_text):
    """Extract all valid searchable keywords from art.txt that will actually return results"""
    
    # Extract exact keywords from the SEARCH KEYWORDS section
    keywords_section = inventory_text.split("=== SEARCH KEYWORDS ===")
    if len(keywords_section) > 1:
        keywords_text = keywords_section[1]
        
        # Parse each category
        countries = []
        styles = []
        colors = []
        themes = []
        
        lines = keywords_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Countries:'):
                countries = [c.strip().lower() for c in line.replace('Countries:', '').split(',')]
            elif line.startswith('Styles:'):
                styles = [s.strip().lower() for s in line.replace('Styles:', '').split(',')]
            elif line.startswith('Colors:'):
                colors = [c.strip().lower() for c in line.replace('Colors:', '').split(',')]
            elif line.startswith('Themes:'):
                themes = [t.strip().lower() for t in line.replace('Themes:', '').split(',')]
    
    # Also extract art piece names and descriptive words
    if "=== COMPLETE INVENTORY ===" in inventory_text and "=== SEARCH KEYWORDS ===" in inventory_text:
        inventory_section = inventory_text.split("=== COMPLETE INVENTORY ===")[1].split("=== SEARCH KEYWORDS ===")[0]
        art_names = []
        descriptive_words = []
        
        # Extract from each art piece
        for line in inventory_section.split('\n'):
            if line.strip() and '. ' in line:
                # Extract art name (before the first ' - ')
                if ' - ' in line:
                    name_part = line.split(' - ')[0]
                    if '. ' in name_part:
                        art_name = name_part.split('. ', 1)[1].strip().lower()
                        art_names.append(art_name)
                        
                        # Extract individual words from art names
                        words = art_name.split()
                        descriptive_words.extend([w for w in words if len(w) > 3])
                    
                    # Extract words from descriptions
                    desc_part = line.split(' - ', 1)[1] if ' - ' in line else ''
                    desc_words = desc_part.lower().split()
                    descriptive_words.extend([w.strip('(),') for w in desc_words if len(w.strip('(),')) > 3])
    else:
        art_names = []
        descriptive_words = []
    
    # Combine all valid keywords
    all_keywords = countries + styles + colors + themes + art_names + list(set(descriptive_words))
    
    # Remove duplicates and filter
    valid_keywords = list(set([k.strip() for k in all_keywords if k.strip() and len(k.strip()) > 2]))
    
    return valid_keywords, countries, styles, colors, themes

# Load art inventory
try:
    with open('art.txt', 'r', encoding='utf-8') as f:
        ART_INVENTORY = f.read()
    logger.info("[SUCCESS] Art inventory loaded successfully")
    logger.info(f"[DATA] Inventory contains {len(ART_INVENTORY.split('==='))-1} art categories")
    
    # Test keyword extraction at startup
    keywords, countries, styles, colors, themes = get_valid_search_keywords_from_inventory(ART_INVENTORY)
    logger.info(f"[KEYWORDS] ✅ Extracted {len(keywords)} total valid search keywords")
    logger.info(f"[KEYWORDS] Countries: {len(countries)} → {countries[:5]}...")
    logger.info(f"[KEYWORDS] Styles: {len(styles)} → {styles}")
    logger.info(f"[KEYWORDS] Colors: {len(colors)} → {colors[:8]}...")
    logger.info(f"[KEYWORDS] Themes: {len(themes)} → {themes[:8]}...")
    logger.info(f"[KEYWORDS] Sample valid keywords: {sorted(keywords)[:20]}")
    
except FileNotFoundError:
    ART_INVENTORY = "Art inventory file not found."
    logger.error("[ERROR] Art inventory file not found")

# Enhanced smart search function
def find_matching_keywords(user_message, inventory_text):
    """Find keywords from user message that match our inventory"""
    user_words = user_message.lower().split()
    inventory_lower = inventory_text.lower()
    message_lower = user_message.lower()
    
    # Extract all searchable keywords from inventory
    matching_keywords = []
    
    # Direct word matching
    for word in user_words:
        if len(word) > 3 and word in inventory_lower:
            matching_keywords.append(word)
    
    return matching_keywords

def find_contextual_art_suggestions(user_message, inventory_text):
    """Find art suggestions based on context, themes, and user intent - ONLY using words from art.txt"""
    message_lower = user_message.lower()
    inventory_lower = inventory_text.lower()
    suggestions = []
    
    # Extract valid search terms from art.txt
    valid_keywords = []
    
    # Countries from art.txt
    countries = ["japan", "china", "korea", "vietnam", "usa", "italy", "france", "germany", "spain", "greece", "brazil", "australia", "canada", "netherlands", "norway", "thailand", "egypt", "india", "turkey", "argentina", "mexico", "finland", "poland", "russia", "iceland", "ukraine", "morocco", "nepal", "belgium", "ireland", "portugal", "israel", "austria", "england", "switzerland", "denmark", "philippines", "myanmar", "hungary", "south africa", "cambodia", "chile", "new zealand"]
    
    # Styles from art.txt
    styles = ["abstract", "modern", "traditional", "landscape", "nature", "urban", "contemporary", "ancient", "geometric", "musical", "surreal", "crystalline"]
    
    # Colors from art.txt
    colors = ["blue", "red", "green", "golden", "purple", "silver", "turquoise", "crimson", "emerald", "azure", "sapphire", "jade", "copper", "pink", "orange"]
    
    # Themes from art.txt
    themes = ["ocean", "sea", "forest", "trees", "desert", "mountains", "city", "night", "dawn", "sunset", "flowers", "water", "snow", "fire", "light", "shadows", "birds", "animals", "stars", "cosmic"]
    
    # Art piece names and descriptive words from art.txt
    art_words = ["celestial", "whispering", "golden", "urban", "azure", "dancing", "mystic", "scarlet", "sunlit", "emerald", "frosted", "wildflowers", "moonlit", "desert", "timeless", "whale", "opal", "forest", "velvet", "harbor", "ancient", "rainfall", "ivory", "rose", "peacock", "starlit", "blushing", "crimson", "marble", "saffron", "silent", "clockwork", "bamboo", "lavender", "porcelain", "opaline", "fireside", "cobalt", "paper", "arctic", "sapphire", "autumn", "lotus", "rustic", "fable", "jade", "carnival", "nebula", "coral", "copper", "maple", "garden", "crystal", "vintage", "seaside", "emerald", "frostbitten", "twilight", "canyon", "papyrus", "willow", "hidden"]
    
    valid_keywords = countries + styles + colors + themes + art_words
    
    # Price-based requests - use actual price values from art.txt
    if any(word in message_lower for word in ['cheap', 'affordable', 'budget', 'inexpensive', 'less expensive', 'lower price']):
        suggestions.append({"trigger": "wildflowers", "reason": "price_request"})  # $1,200 piece
    elif any(word in message_lower for word in ['expensive', 'premium', 'luxury', 'high-end', 'costly']):
        suggestions.append({"trigger": "dancing", "reason": "premium_request"})  # $3,700 piece
    
    # Regional/Cultural connections - only using valid countries
    if any(word in message_lower for word in ['asia', 'asian', 'orient', 'eastern']):
        if 'lotus' in message_lower:
            suggestions.append({"trigger": "lotus", "reason": "asian_lotus_theme"})
        else:
            suggestions.append({"trigger": "japan", "reason": "asian_culture"})
    
    # Direct country matches
    for country in countries:
        if country in message_lower:
            suggestions.append({"trigger": country, "reason": f"{country}_request"})
            break
    
    # Direct style matches
    for style in styles:
        if style in message_lower:
            suggestions.append({"trigger": style, "reason": f"{style}_style"})
            break
    
    # Direct color matches
    for color in colors:
        if color in message_lower:
            suggestions.append({"trigger": color, "reason": f"{color}_color"})
            break
    
    # Direct theme matches
    for theme in themes:
        if theme in message_lower:
            suggestions.append({"trigger": theme, "reason": f"{theme}_theme"})
            break
    
    # Nature/peaceful themes using valid words
    if any(word in message_lower for word in ['calm', 'peaceful', 'serene', 'tranquil', 'relax']):
        suggestions.append({"trigger": "moonlit", "reason": "peaceful_mood"})
    
    if any(word in message_lower for word in ['color', 'colorful', 'bright', 'vibrant']):
        suggestions.append({"trigger": "carnival", "reason": "colorful_request"})
    
    # General conversation redirects - using valid art words
    if not suggestions and len(message_lower) > 5:
        if any(word in message_lower for word in ['hello', 'hi', 'good', 'nice', 'beautiful']):
            suggestions.append({"trigger": "celestial", "reason": "welcome_showcase"})
        elif any(word in message_lower for word in ['help', 'show', 'see', 'find']):
            suggestions.append({"trigger": "golden", "reason": "browsing_assistance"})
        else:
            suggestions.append({"trigger": "mystic", "reason": "general_interest"})
    
    # Validate all suggestions use words from art.txt - get fresh keywords
    fresh_keywords = get_valid_search_keywords()
    validated_suggestions = []
    
    for suggestion in suggestions:
        trigger_lower = suggestion["trigger"].lower()
        if trigger_lower in fresh_keywords:
            validated_suggestions.append(suggestion)
            logger.info(f"[VALIDATION] ✅ Approved trigger: '{suggestion['trigger']}'")
        else:
            # Try to find a close match
            close_matches = [k for k in fresh_keywords if trigger_lower in k or k in trigger_lower]
            if close_matches:
                # Replace with the closest match
                suggestion["trigger"] = close_matches[0]
                validated_suggestions.append(suggestion)
                logger.info(f"[VALIDATION] ✅ Replaced '{trigger_lower}' with '{close_matches[0]}'")
            else:
                logger.warning(f"[VALIDATION] ❌ Rejected trigger '{suggestion['trigger']}' - not in art.txt keywords")
    
    return validated_suggestions

# Intelligent shopkeeper system prompt (built from centralized module)
SYSTEM_PROMPT = build_shopkeeper_system_prompt(ART_INVENTORY)

@app.route('/health', methods=['GET'])
def health():
    """Simple health check for uptime and inventory availability."""
    logger.info("[HEALTH] Health check requested")
    return jsonify({
        "status": "healthy", 
        "agent_available": False,  # Using simple OpenAI mode
        "inventory_loaded": ART_INVENTORY != "Art inventory file not found."
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main chat endpoint.

    Accepts a JSON body with a `message` field. Builds a system prompt from
    inventory, calls OpenAI, parses optional search triggers, and returns a
    cleaned response plus any web actions for the frontend to dispatch.
    """
    logger.info("[CHAT] Chat request received")
    
    # Handle CORS preflight OPTIONS request
    if request.method == 'OPTIONS':
        logger.info("[CORS] Handling OPTIONS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            logger.error("[ERROR] No JSON data in request")
            return jsonify({"error": "No data provided"}), 400
        
        user_message = data.get("message")
        if not user_message:
            logger.error("[ERROR] No message in request")
            return jsonify({"error": "No message provided"}), 400
        
        # Log the incoming user message
        chat_logger.info(f"[USER] {user_message}")
        logger.info(f"[PROCESSING] User message: {user_message[:100]}...")
        
        # Check for matching keywords in inventory
        matching_keywords = find_matching_keywords(user_message, ART_INVENTORY)
        logger.info(f"[MATCH] Found matching keywords in inventory: {matching_keywords}")
        
        # Find contextual art suggestions
        contextual_suggestions = find_contextual_art_suggestions(user_message, ART_INVENTORY)
        logger.info(f"[CONTEXT] Found contextual suggestions: {contextual_suggestions}")
        
        # Use Intelligent OpenAI Shopkeeper
        logger.info("[AI] Using Intelligent OpenAI Shopkeeper...")
        chat_logger.info("[SYSTEM] Using Intelligent OpenAI Shopkeeper")
        
        # First pass: conversational answer with ONE main suggestion
        first_pass_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_first_pass_user_prompt(user_message)},
        ]

        logger.info(f"[API] First pass to OpenAI: {OPENAI_MODEL}")
        openai_response_1 = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=first_pass_messages,
            max_tokens=int(os.getenv("MAX_TOKENS", "300")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
        )

        bot_response = openai_response_1.choices[0].message.content
        logger.info(f"[SUCCESS] OpenAI response received: {len(bot_response)} characters")
        logger.info(f"[PREVIEW] Raw response preview: {bot_response[:100]}...")
        
        # Log the raw bot response (stdout only)
        chat_logger.info(f"[BOT_RAW] {bot_response}")
        
        # Second pass: pick exactly one valid keyword based on the first suggestion
        valid_keywords, *_ = get_valid_search_keywords_from_inventory(ART_INVENTORY)
        selector_system = build_keyword_selector_system_prompt(valid_keywords)
        second_pass_messages = [
            {"role": "system", "content": selector_system},
            {"role": "user", "content": f"Answer to analyze:\n{bot_response}"},
        ]

        logger.info("[API] Second pass (keyword selector)")
        openai_response_2 = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=second_pass_messages,
            max_tokens=8,
            temperature=0,
        )

        raw_keyword = (openai_response_2.choices[0].message.content or "").strip().lower()
        # Validate keyword against the extracted set
        kws_set = set(k.lower() for k in valid_keywords)
        keyword = raw_keyword if raw_keyword in kws_set else ""
        if not keyword and raw_keyword:
            # try closest partial match
            partial = [k for k in kws_set if raw_keyword in k or k in raw_keyword]
            keyword = partial[0] if partial else ""

        web_actions = []
        if keyword:
            web_actions = [
                {"type": "search", "value": keyword},
                {"type": "scroll", "value": "art-collection"},
            ]
            logger.info(f"[TRIGGER] Using keyword: {keyword}")
            chat_logger.info(f"[TRIGGER] {{'type': 'search', 'value': '{keyword}'}}")
        else:
            logger.info("[TRIGGER] No valid keyword selected")
            chat_logger.info("[CHAT] No search triggers")
        
        # No need to clean triggers; first-pass output contains none by design
        clean_response = bot_response.strip()
        
        response_data = {
            "response": clean_response,
            "web_actions": web_actions,
            "art_suggestions": [],
            "status": "success",
            "agent_used": False
        }
        
        # Log final response
        logger.info(f"[RESPONSE] Sending: {len(response_data['response'])} chars, {len(response_data['web_actions'])} actions")
        chat_logger.info(f"[FINAL] {response_data}")
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as openai_error:
        error_message = str(openai_error)
        logger.error(f"[ERROR] OpenAI Error: {error_message}")
        chat_logger.error(f"[ERROR] {error_message}")
        
        if "authentication" in error_message.lower():
            logger.error("[ERROR] OpenAI authentication failed")
            return jsonify({"error": "Invalid API key"}), 401
        elif "rate limit" in error_message.lower():
            logger.error("[ERROR] OpenAI rate limit exceeded")
            return jsonify({"error": "Rate limit exceeded"}), 429
        else:
            logger.error(f"[ERROR] OpenAI API error: {error_message}")
            return jsonify({"error": f"OpenAI API error: {error_message}"}), 500
    except Exception as e:
        logger.error(f"[ERROR] General error in chat: {str(e)}")
        chat_logger.error(f"[ERROR] {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def get_valid_search_keywords():
    """Extract all valid searchable keywords from art.txt that will actually return results"""
    keywords, _, _, _, _ = get_valid_search_keywords_from_inventory(ART_INVENTORY)
    return keywords

def parse_search_triggers(response_text):
    """Parse SEARCH_TRIGGER commands from LLM response - STRICT validation against art.txt"""
    web_actions = []
    
    logger.info("[PARSE] Parsing search triggers from response...")
    
    # Get valid keywords from art.txt
    valid_keywords = get_valid_search_keywords()
    
    # Look for SEARCH_TRIGGER: pattern
    if "SEARCH_TRIGGER:" in response_text:
        logger.info("[PARSE] SEARCH_TRIGGER found in response!")
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if "SEARCH_TRIGGER:" in line:
                # Extract the search term after SEARCH_TRIGGER:
                search_term = line.split("SEARCH_TRIGGER:")[1].strip().lower()
                
                # STRICT validation - search term must be in our extracted keywords
                if search_term in valid_keywords:
                    web_actions.append({"type": "search", "value": search_term})
                    web_actions.append({"type": "scroll", "value": "art-collection"})
                    logger.info(f"[PARSE] ✅ VALID search term: '{search_term}' (found in art.txt keywords)")
                else:
                    # Check for partial matches within valid keywords
                    partial_matches = [k for k in valid_keywords if search_term in k or k in search_term]
                    if partial_matches:
                        best_match = partial_matches[0]  # Use first match
                        web_actions.append({"type": "search", "value": best_match})
                        web_actions.append({"type": "scroll", "value": "art-collection"})
                        logger.info(f"[PARSE] ✅ PARTIAL match: '{search_term}' → using '{best_match}'")
                    else:
                        logger.warning(f"[PARSE] ❌ REJECTED search term: '{search_term}' (NOT in art.txt keywords)")
                        logger.info(f"[PARSE] Available keywords: {valid_keywords[:10]}... ({len(valid_keywords)} total)")
                
                break  # Only one search per response
    else:
        logger.info("[PARSE] No SEARCH_TRIGGER found - casual conversation")
    
    return web_actions

def clean_search_triggers(response_text):
    """Remove SEARCH_TRIGGER commands from response text"""
    logger.info("[CLEAN] Cleaning search triggers from response...")
    
    lines = response_text.split('\n')
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        if "SEARCH_TRIGGER:" not in line:
            cleaned_lines.append(line)
        else:
            removed_count += 1
            logger.info(f"[CLEAN] Removed trigger line: {line.strip()}")
    
    cleaned_response = '\n'.join(cleaned_lines).strip()
    logger.info(f"[CLEAN] Cleaned response: {len(cleaned_response)} chars (removed {removed_count} trigger lines)")
    
    return cleaned_response

if __name__ == '__main__':
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("[ERROR] OPENAI_API_KEY not found in .env file!")
        exit(1)
    
    port = int(os.getenv("PORT", "5000"))
    logger.info(f"[START] Starting Artisty Backend Server on port {port}")
    logger.info(f"[START] API available at: http://localhost:{port}/api/chat")
    logger.info(f"[START] Health check: http://localhost:{port}/health")
    
    app.run(host='localhost', port=port, debug=True)
