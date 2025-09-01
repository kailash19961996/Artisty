# Artisty

**Agentic AI-powered art gallery with intelligent search, conversational assistance, and real-time actions**

Artisty transforms art discovery and purchase by combining intelligent conversational AI with a curated gallery experience. Users can naturally describe what they're looking for and receive personalized recommendations with real-time gallery navigation, cart management, and interactive actions—all through natural conversation.

## Problem Statement

Traditional art galleries and e-commerce platforms rely on basic filters and keyword search, making art discovery frustrating and limiting. Users struggle to find pieces that match their aesthetic preferences, budget, or specific requirements using conventional search methods.

## Live Demo
[Visit the Artisty Website](https://main.d22zce484yggk5.amplifyapp.com/)

## Screenshots

### Main Page
![Main Page](frontend/docs/images/main-page.png)

### Agent in Action
![Agent helping the user navigate artworks](frontend/docs/images/agent-navigate.png)


## Architecture Overview

The system uses a multi-agent approach with LangChain orchestration:

1. **Intent Router**: Classifies user messages as information requests or art suggestions
2. **Inventory Search Agent**: Intelligently searches the art collection using LLM understanding
3. **Response Generator**: Creates conversational responses with appropriate suggestions
4. **Extraction Agent**: Identifies mentioned artwork names for gallery navigation
5. **Memory Manager**: Maintains conversation context for better user experience

All decision-making is handled by AI agents rather than manual rules, ensuring intelligent and flexible responses to user queries.

## What It Can Do

- **Natural Language Search**: Ask for art using everyday language like "show me vibrant pieces from Asia under $2000"
- **Intelligent Recommendations**: AI analyzes your preferences and suggests 1-10+ relevant artworks
- **Real-time Streaming Responses**: Word-by-word streaming with immediate actions
- **Agentic Actions**: AI automatically navigates gallery, opens popups, adds to cart, and manages checkout
- **Smart Cart Management**: "Show me my cart" → AI opens cart page and provides status
- **Regional Understanding**: Knows geographic mappings (Asia = Japan, China, Korea, Thailand, India, Vietnam, etc.)
- **Conversational Memory**: Remembers context within conversations for better assistance
- **Real-time Gallery Navigation**: Automatically scrolls and displays suggested artworks
- **Interactive UI Control**: AI controls quick-view popups, cart operations, and page navigation
- **Inventory-Aware Responses**: Only suggests available pieces from the actual collection

## What It Cannot Do

- Generate or create new artworks
- Process payments or handle transactions
- Provide art authentication or provenance verification
- Access external art databases or inventories
- Remember preferences across different browser sessions
- Suggest artworks not in the current inventory

## Technology Stack

### Frontend
- **React 18** with Vite for fast development and building
- **Modern CSS** with custom components and responsive design
- **Real-time Chat Interface** with structured message rendering
- **Hosted on AWS Amplify** with automatic CI/CD from GitHub

### Backend
- **AWS Lambda (Python 3.11)** serverless functions with streaming SSE support
- **API Gateway** REST API with CORS-enabled endpoints (`/api/health`, `/api/chat/stream`)
- **Lambda Layers** (OpenAI, LangChain, Pydantic) packaged with Docker for Linux compatibility
- **LangChain Agents** with structured tools for UI actions (quick_view, add_to_cart, navigate, checkout)
- **OpenAI GPT-4o-mini** for natural language understanding and agentic decision-making
- **Server-Sent Events (SSE)** for real-time streaming responses
- **CloudWatch** for logging and monitoring

### Deployment & Infra
- **S3** for Lambda layer storage
- **CloudWatch** for monitoring/logging
- **AWS IAM** for security and access control
- **Amplify** for frontend hosting & environment management

### Architecture
- **Agentic Tool System** with real-time UI control (navigation, cart, popups)
- **Streaming Response Pipeline** with word-by-word delivery and immediate actions
- **Intent Classification** for routing between information, suggestions, and UI actions
- **LLM-Powered Extraction** for artwork name identification and action triggers
- **Responsive Layout** with chatbot integration (30% chat, 70% content on desktop)

## Quick Start

### Backend Setup - Local
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

python main.py
```

### Frontend Setup - Local
```bash
cd frontend
npm install

# Create .env for API endpoint
echo "VITE_API_BASE=http://127.0.0.1:5000" > .env

npm run dev
```

### Production Deployment
```bash
# Set environment variable in AWS Amplify Console:
# VITE_API_BASE=https://your-api-gateway-url.execute-api.region.amazonaws.com/prod/api

# Deploy automatically via GitHub integration
```

## How Search Works in Frontend

The frontend implements intelligent search through multiple mechanisms:

### **1. Chatbot-Triggered Search**
- AI agent analyzes user requests and extracts artwork names
- Names are sent as space-separated pairs to the frontend
- Frontend treats these as explicit selections and displays only those artworks in the suggested order
- Example: Agent suggests "neon pride jungle rhythm" → Frontend shows those exact 2 artworks

### **2. Manual Search Bar**
- Users can type directly in the search bar
- Combines semantic search (AI-powered understanding) with keyword fallback
- Semantic search finds top 5 relevant pieces based on meaning and context
- Keyword search provides additional matches for comprehensive results
- Auto-scrolls to gallery section when search is performed

## Example Interactions

**Regional Search with Actions:**
- "What do you have from the UK?" → AI searches UK art + auto-scrolls to gallery
- "Show me pieces from Asia" → Streams response + displays Japan, China, Korea, Thailand, India, Vietnam artworks

**Interactive Shopping:**
- "Add Neon Pride to my cart" → AI adds artwork + shows cart animation + confirms
- "Show me my cart" → AI navigates to cart page + provides status
- "I want to see Golden Gaze closer" → AI opens quick-view popup

**Streaming Conversations:**
- "I want something blue and calming" → Streams word-by-word response + suggests blue artworks
- "What's available under $1500?" → Real-time filtering + immediate gallery update
- "Take me to checkout" → AI navigates to cart + initiates checkout process

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

