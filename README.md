# Artisty

**Agentic AI-powered art gallery with intelligent search and conversational assistance**

Artisty transforms the way people discover and purchase art by combining intelligent conversational AI agent with a curated gallery experience. Instead of traditional keyword search, users can naturally describe what they're looking for and receive personalized recommendations with real-time gallery navigation.

## Problem Statement

Traditional art galleries and e-commerce platforms rely on basic filters and keyword search, making art discovery frustrating and limiting. Users struggle to find pieces that match their aesthetic preferences, budget, or specific requirements using conventional search methods.

## Live Demo
[Visit the Artisty Website](https://main.d22zce484yggk5.amplifyapp.com/)

## Screenshots

### Main Page
![Main Page](docs/images/main-page.png)

### Agent in Action
![Agent helping the user navigate artworks](docs/images/agent-navigate.png)


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
- **Regional Understanding**: Knows geographic mappings (Asia = Japan, China, Korea, Thailand, India, Vietnam, etc.)
- **Conversational Memory**: Remembers context within conversations for better assistance
- **Real-time Gallery Navigation**: Automatically scrolls and displays suggested artworks
- **Inventory-Aware Responses**: Only suggests available pieces from the actual collection
- **Multi-criteria Filtering**: Simultaneously search by country, color, style, theme, and price

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
- **AWS Lambda (Python 3.11)** serverless functions
- **API Gateway** as the HTTP entry point (replaces Flask API server)
- **Lambda Layers** (OpenAI, LangChain, Pydantic) packaged with Docker & S3 for Linux compatibility
- **LangChain** for AI agent orchestration and memory management
- **OpenAI GPT-4o-mini** for natural language understanding and generation
- **CloudWatch** for logging and monitoring

### Deployment & Infra
- **S3** for Lambda layer storage
- **CloudWatch** for monitoring/logging
- **AWS IAM** for security and access control
- **Amplify** for frontend hosting & environment management

### Architecture
- **Smart Agent System** with conversation memory and tool usage
- **Intent Classification** to route between information and suggestions
- **LLM-Powered Extraction** for artwork name identification
- **Structured Response Rendering** with numbered lists and conclusions

## Quick Start

### Backend Setup
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

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 to start exploring the gallery.

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

**Regional Search:**
- "What do you have from the UK?" → Shows only UK/England artworks
- "Show me pieces from Asia" → Displays artworks from Japan, China, Korea, Thailand, India, Vietnam

**Style and Color:**
- "I want something blue and calming" → Suggests blue-toned, serene pieces
- "Show me vibrant abstract art" → Recommends colorful, energetic abstract works

**Price and Preference:**
- "What's available under $1500?" → Lists artworks within budget
- "I need something for my office" → Suggests professional, sophisticated pieces

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

