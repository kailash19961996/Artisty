# Artisty

**Reimagining E-shopping experience with AI Agents powered by LangChain, deployed on AWS**

Artisty is a full‑stack, multi‑agent platform hosted on AWS that transforms how people explore and purchase art. It solves the frustration of clunky filters by enabling natural conversations that surface the right pieces instantly. With intelligent search and real‑time gallery actions, it delivers a vision of seamless, personalized art discovery.

Try it yourself at [www.artisty.shop](https://artisty.shop/)

### Main Page
![Main Page](frontend/docs/images/main-page.png)

### Agent in Action
![Agent helping the user navigate artworks](frontend/docs/images/agent-navigate.png)

[CLICK HERE FOR DEMO VIDEO](https://youtu.be/kAlLpC9a_uQ)

[LEAVE YOUR FEEDBACK HERE](https://citrine-hamburger-7f5.notion.site/26f19d49e5c18076a3e4f4318f512ff5?pvs=105)

### Technical Features

| Tech | Description |
|---------|-------------|
| <span style="color:red; font-weight:bold;">OpenAI API</span> | For LLM support |
| <span style="color:red; font-weight:bold;">Langchain</span> | For tool usage and agent orchestation |
| <span style="color:red; font-weight:bold;">AWS Route 52</span> | Domain, routing and metrics |
| <span style="color:red; font-weight:bold;">AWS Amplify - React + JS - Frontend</span> | Modern, type-safe UI, deployed on AWS Amplify |
| <span style="color:red; font-weight:bold;">AWS Lambda - Python - Backend</span> | Python-based serverless, scalable architecture |
| <span style="color:red; font-weight:bold;">Amazon S3</span> | Used to package Lambda layers |
| <span style="color:red; font-weight:bold;">AWS API Gateway</span> | Manages secure connections between frontend and backend |
| <span style="color:red; font-weight:bold;">AWS DynamoDB Database</span> | High-performance NoSQL storage for tickets and messages |
| <span style="color:red; font-weight:bold;">CloudWatch</span> | For logging and monitoring |
| <span style="color:red; font-weight:bold;">Docker</span> | Used to package Lambda layers |
| <span style="color:red; font-weight:bold;">Real-time Updates</span> | Optimistic UI with backend synchronization |
| <span style="color:red; font-weight:bold;">CORS Support</span> | Secure API access |
| <span style="color:red; font-weight:bold;">Github Action</span> | For CI/CD |



## Architecture Overview

The system uses a multi-agent approach with LangChain orchestration:

1. **Intent Router**: Classifies user messages as information requests or art suggestions
2. **Inventory Search Agent**: Intelligently searches the art collection using LLM understanding
3. **Response Generator**: Creates conversational responses with appropriate suggestions
4. **Extraction Agent**: Identifies mentioned artwork names for gallery navigation
5. **Memory Manager**: Maintains conversation context for better user experience

### Agent Architecture
<img width="3840" height="2628" alt="Untitled diagram _ Mermaid Chart-2025-09-15-165451" src="https://github.com/user-attachments/assets/4018f647-cd4c-443f-a482-2fc17e9ddd4c" />

![Mermaid Chart - Create complex, visual diagrams with text  A smarter way of creating diagrams -2025-09-15-164803](https://github.com/user-attachments/assets/37b1f32f-fdf3-48eb-89f0-eefccc99515a)

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
- Provide art authentication or provenance verification
- Access external art databases or inventories
- Remember preferences across different browser sessions
- Suggest artworks not in the current inventory

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

