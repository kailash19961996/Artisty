"""LangChain-based smart store assistant for Artisty gallery - Lambda version.

The assistant knows the inventory, can answer questions, and suggest artworks.
Uses conversation memory and proper intent routing.
Optimized for AWS Lambda deployment.
"""

from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent


@dataclass
class ArtworkSuggestion:
    """Structured artwork suggestion"""
    names: List[str]  # List of artwork names to search for
    intent: str  # "art_suggestion", "general_info", "both"
    response: str  # Assistant's response text


class ArtistryAssistant:
    """Smart gallery assistant with inventory knowledge and memory - Lambda optimized"""
    
    def __init__(self, inventory_text: str, model_name: str = "gpt-4o-mini", openai_api_key: str = None):
        self.inventory_text = inventory_text
        self.model_name = model_name
        
        # Initialize OpenAI client with provided API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Extract artwork names from inventory for reference
        self.artwork_names = self._extract_artwork_names()
        
        # Create tools
        self.tools = [
            Tool(
                name="search_inventory",
                description="Search inventory for artworks matching criteria (country, color, style, price)",
                func=self._search_inventory_tool
            ),
            Tool(
                name="list_countries", 
                description="List all countries represented in the gallery inventory",
                func=self._list_countries_tool
            ),
            Tool(
                name="get_artwork_details",
                description="Get details about a specific artwork by name",
                func=self._get_artwork_details_tool
            )
        ]
        
        # Create the agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3
        )
    
    def _extract_artwork_names(self) -> List[str]:
        """Extract artwork names from inventory"""
        names = []
        for line in self.inventory_text.splitlines():
            line = line.strip()
            if ". " in line and " - " in line:
                left = line.split(" - ")[0]
                if ". " in left:
                    name = left.split(". ", 1)[1].strip()
                    if name:
                        names.append(name)
        return names
    
    def _create_agent(self):
        """Create the LangChain agent with proper prompts"""
        
        system_prompt = f"""You are Purple, a knowledgeable and witty assistant for Artisty, an online art gallery. 

Your personality: Friendly, helpful, with a touch of humor. You're like a smart gallery curator who knows every piece in the collection.

INVENTORY KNOWLEDGE:
{self.inventory_text}

CAPABILITIES:
1. Answer general questions about the gallery, policies, shipping, etc.
2. Suggest artworks based on user preferences (country, color, style, price, themes)
3. Provide detailed information about specific artworks
4. List countries and artists represented

IMPORTANT RULES:
- For country/region requests, be STRICT about filtering. If user asks for "UK" or "United Kingdom", only suggest items from UK/England.
- When suggesting artworks, let the search results determine how many to show (could be 1-10+ depending on what matches)
- Don't artificially limit suggestions - if there are 8 great matches, show all 8
- If there are only 2 perfect matches, show just those 2
- Always be helpful and engaging
- Use the tools available to search inventory and provide accurate information

COUNTRY MAPPINGS (be exact):
- UK/United Kingdom/Britain/English = England, UK (from inventory)
- Europe = England, UK, France, Italy, Spain, Portugal, Netherlands, Germany, Norway, Ireland, Poland, Austria, Hungary, Denmark, Switzerland, Greece, Iceland, Finland, Turkey
- Asia = Japan, China, Korea, Thailand, India, Vietnam, Turkey  
- Africa = South Africa, Egypt, Morocco
- North America = USA, Canada
- South America = Brazil, Argentina
- Oceania = Australia, New Zealand

When suggesting artworks, format your response with:
1. A witty acknowledgment
2. Numbered list of 1-5 artworks with: Name - Price (Country) - Brief description
3. A concluding suggestion

Remember: You have access to tools to search the inventory and get specific details."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)
    
    def _search_inventory_tool(self, query: str) -> str:
        """LLM-powered intelligent inventory search that understands user intent"""
        
        search_prompt = f"""You are an expert gallery curator searching through an art inventory based on user criteria.

USER QUERY: {query}

FULL INVENTORY:
{self.inventory_text}

INSTRUCTIONS:
1. Understand what the user is looking for (country/region, color, style, theme, price range, etc.)
2. For regions like "Asia", find ALL countries that belong to that region (Japan, China, Korea, Thailand, India, Vietnam, etc.)
3. For colors, find artworks whose descriptions mention those colors
4. For styles/themes, look for matching descriptive elements
5. Suggest between 1-10 artworks that best match the criteria (don't limit artificially)
6. Format as: "Found X matching artworks:" followed by the full inventory lines
7. If no matches, explain why and suggest alternatives

Be intelligent about regional mappings:
- Asia = Japan, China, Korea, Thailand, India, Vietnam, Turkey
- Europe = UK, England, France, Italy, Spain, Portugal, Netherlands, Germany, Norway, Ireland, Poland, Austria, Hungary, Denmark, Switzerland, Greece, Iceland, Finland, Turkey
- Africa = South Africa, Egypt, Morocco
- Americas = USA, Canada, Brazil, Argentina, Chile, Mexico
- Oceania = Australia, New Zealand

Return the matching inventory lines exactly as they appear."""

        try:
            result = self.llm.invoke(search_prompt)
            return result.content.strip()
        except Exception as e:
            return f"Search error: {str(e)}. Please try a different query."
    
    def _list_countries_tool(self, query: str = "") -> str:
        """Tool to list all countries in inventory"""
        countries = set()
        for line in self.inventory_text.splitlines():
            if " - $" in line and "(" in line and ")" in line:
                # Extract country from format: Name - $Price (Country) - Description
                try:
                    country_part = line.split("(")[1].split(")")[0].strip()
                    countries.add(country_part)
                except:
                    continue
        
        sorted_countries = sorted(list(countries))
        return f"Countries represented in our gallery ({len(sorted_countries)} total):\n" + "\n".join(f"{i+1}. {country}" for i, country in enumerate(sorted_countries))
    
    def _get_artwork_details_tool(self, artwork_name: str) -> str:
        """Tool to get details about a specific artwork"""
        for line in self.inventory_text.splitlines():
            if artwork_name.lower() in line.lower() and " - $" in line:
                return f"Artwork details: {line.strip()}"
        return f"Artwork '{artwork_name}' not found in inventory."
    
    def process_message(self, user_message: str) -> ArtworkSuggestion:
        """Process user message and return structured response"""
        
        # Get response from agent
        try:
            result = self.agent_executor.invoke({"input": user_message})
            response_text = result.get("output", "I apologize, but I encountered an error processing your request.")
        except Exception as e:
            response_text = f"I'm having a bit of trouble right now. Let me try to help you directly! {str(e)}"
        
        # Determine intent and extract artwork names
        intent = self._classify_intent(user_message, response_text)
        artwork_names = []
        
        if intent in ["art_suggestion", "both"]:
            artwork_names = self._extract_suggested_artworks(response_text)
        
        return ArtworkSuggestion(
            names=artwork_names,
            intent=intent,
            response=response_text
        )
    
    def _classify_intent(self, user_message: str, response: str) -> str:
        """LLM-powered intent classification based on user message and assistant response"""
        
        classification_prompt = f"""You are analyzing a conversation between a user and an art gallery assistant.

USER MESSAGE: {user_message}
ASSISTANT RESPONSE: {response}

Classify the intent into one of these categories:
- "art_suggestion": The assistant suggested specific artworks for the user to view/purchase
- "general_info": The assistant provided general information, policy details, greetings, or other non-product info
- "both": The assistant both answered a question AND suggested specific artworks

Look for mentions of specific artwork names in the response to determine if suggestions were made.

Rules:
- If the response contains specific artwork names (like "Neon Pride", "Golden Gaze", etc.), it's likely "art_suggestion"
- If it's just answering questions about policies, countries, greetings, etc. without artwork names, it's "general_info"
- If it does both, classify as "both"

Respond with ONLY the classification: art_suggestion, general_info, or both"""

        try:
            result = self.llm.invoke(classification_prompt)
            intent = result.content.strip().lower()
            
            if intent in ["art_suggestion", "general_info", "both"]:
                return intent
            
            # Fallback - check if response contains artwork names
            response_lower = response.lower()
            has_artwork_names = any(name.lower() in response_lower for name in self.artwork_names[:30])
            return "art_suggestion" if has_artwork_names else "general_info"
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            # Simple fallback
            response_lower = response.lower()
            has_artwork_names = any(name.lower() in response_lower for name in self.artwork_names[:30])
            return "art_suggestion" if has_artwork_names else "general_info"
    
    def _extract_suggested_artworks(self, response_text: str) -> List[str]:
        """Extract artwork names from response using LLM - no manual limits"""
        
        extraction_prompt = f"""From the following art gallery assistant response, extract ONLY the artwork names that were suggested.

Rules:
- Extract only the artwork names (usually 2-3 words each like "Neon Pride" or "Golden Gaze")
- Return them as a simple list, one per line
- No prices, countries, or descriptions
- Extract ALL suggested artworks, don't limit the number
- If no artworks were suggested, return "NONE"

Response to analyze:
{response_text}

Extracted artwork names:"""

        try:
            extraction_result = self.llm.invoke(extraction_prompt)
            extracted_text = extraction_result.content.strip()
            
            if extracted_text.upper() == "NONE" or not extracted_text:
                return []
            
            # Clean and filter the extracted names - let LLM decide the count
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            valid_names = []
            
            for line in lines:
                # Remove numbering, bullets, etc.
                clean_line = line.split('. ', 1)[-1].split('- ', 1)[-1].strip()
                if clean_line and len(clean_line.split()) <= 4:  # Reasonable artwork name length
                    valid_names.append(clean_line)
            
            return valid_names  # No artificial limit - let LLM decide
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return []


def load_art_inventory() -> str:
    """Load art inventory from file"""
    try:
        # Try different possible locations
        for path in ["art.txt", "./art.txt", "/opt/art.txt"]:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                continue
        return "Art inventory file not found."
    except Exception as e:
        return f"Error loading inventory: {str(e)}"


def create_assistant(openai_api_key: str = None) -> ArtistryAssistant:
    """Create and initialize the assistant"""
    inventory = load_art_inventory()
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    return ArtistryAssistant(
        inventory_text=inventory,
        model_name=model_name,
        openai_api_key=openai_api_key
    )
