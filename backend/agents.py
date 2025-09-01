"""LangChain-based smart store assistant for Artisty gallery.

The assistant knows the inventory, can answer questions, and suggest artworks.
Uses conversation memory and proper intent routing.
"""

from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langchain.tools import Tool, StructuredTool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from pydantic import BaseModel, Field
import re


@dataclass
class ArtworkSuggestion:
    """Structured artwork suggestion"""
    names: List[str]  # List of artwork names to search for
    intent: str  # "art_suggestion", "general_info", "both"
    response: str  # Assistant's response text
    web_actions: List[Dict[str, str]]  # Web actions for frontend


class ArtistryAssistant:
    """Smart gallery assistant with inventory knowledge and memory"""
    
    def __init__(self, inventory_text: str, model_name: str = "gpt-4o-mini"):
        self.inventory_text = inventory_text
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000  # Keep more conversation history
        )
        
        # Extract artwork names from inventory for reference
        self.artwork_names = self._extract_artwork_names()
        
        # Schemas for structured tools
        class QuickViewInput(BaseModel):
            artwork_name: str = Field(..., description="Exact artwork name to open in quick view")

        class AddToCartInput(BaseModel):
            artwork_name: str = Field(..., description="Exact artwork name to add to cart")

        class NavigateInput(BaseModel):
            destination: Literal["cart", "home"] = Field(..., description="Where to navigate: 'cart' or 'home'")

        class EmptyInput(BaseModel):
            pass

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
            ),
            StructuredTool.from_function(
                name="quick_view",
                description="Open a quick-view popup for a specific artwork when the user asks to zoom or view.",
                func=self._quick_view_artwork_tool,
                args_schema=QuickViewInput,
            ),
            StructuredTool.from_function(
                name="add_to_cart",
                description="Add a specific artwork to the user's shopping cart.",
                func=self._add_to_cart_tool,
                args_schema=AddToCartInput,
            ),
            StructuredTool.from_function(
                name="navigate",
                description="Navigate the UI to either the cart or the home (gallery) page.",
                func=self._navigate_tool,
                args_schema=NavigateInput,
            ),
            StructuredTool.from_function(
                name="proceed_to_checkout",
                description="Start the checkout process for items in the cart.",
                func=self._proceed_to_checkout_tool,
                args_schema=EmptyInput,
            ),
        ]
        
        # Create the agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
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

UI ACTIONS AND TOOLS (MANDATORY):
- You have tools: quick_view(artwork_name), add_to_cart(artwork_name), navigate(destination in [cart, home]), proceed_to_checkout().
- If the user asks to zoom/enlarge/show popup → call quick_view.
- If the user asks to bag/add/buy → call add_to_cart with the correct artwork name.
- If the user asks to go to cart/home → call navigate with the destination.
- If the user asks to pay/checkout → call proceed_to_checkout.
- NEVER claim an action is completed unless you have called the appropriate tool.

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
    
    def _quick_view_artwork_tool(self, artwork_name: str) -> str:
        """Tool to show quick view popup of an artwork"""
        return f"Showing quick view for {artwork_name}."
    
    def _add_to_cart_tool(self, artwork_name: str) -> str:
        """Tool to add artwork to cart"""
        return f"Added {artwork_name} to the cart."
    
    def _navigate_tool(self, destination: str) -> str:
        """Tool to navigate to a destination ('cart' or 'home')"""
        if destination not in {"cart", "home"}:
            destination = "home"
        return f"Navigating to {destination}."
    
    def _proceed_to_checkout_tool(self) -> str:
        """Tool to start checkout process"""
        return "Proceeding to checkout."
    
    def process_message(self, user_message: str) -> ArtworkSuggestion:
        """Process user message and return structured response"""
        return self._process_message_sync(user_message)
    
    def process_message_stream(self, user_message: str):
        """Process user message with streaming response"""
        try:
            # Get response from agent with streaming
            result = self.agent_executor.invoke({"input": user_message})
            response_text = result.get("output", "I apologize, but I encountered an error processing your request.")
            
            # Determine intent and extract artwork names
            intent = self._classify_intent(user_message, response_text)
            artwork_names = []
            
            if intent in ["art_suggestion", "both"]:
                artwork_names = self._extract_suggested_artworks(response_text)
            
            # Build web actions from intermediate tool steps
            steps = result.get("intermediate_steps", [])
            web_actions = self._actions_from_steps(steps)
            
            # Add default search action ONLY when it's a pure suggestion
            has_imperative = any(a.get("type") in ["add_to_cart", "quick_view", "navigate", "checkout"] for a in web_actions)
            if not has_imperative and artwork_names and intent in ["art_suggestion", "both"]:
                search_string = " ".join(artwork_names).lower()
                if not any(action.get("type") == "search" for action in web_actions):
                    web_actions.append({"type": "search", "value": search_string})
                    web_actions.append({"type": "scroll", "value": "art-collection"})
            
            # Send actions immediately if available (before streaming text)
            actions_sent = False
            if web_actions:
                yield {
                    "chunk": "",
                    "is_complete": False,
                    "web_actions": web_actions,
                    "intent": intent,
                    "suggested_artworks": artwork_names,
                    "full_response": None,
                    "actions_only": True  # Flag to indicate this is an actions-only chunk
                }
                actions_sent = True
            
            # Stream the response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                chunk_data = {
                    "chunk": word + " ",
                    "is_complete": i == len(words) - 1,
                    "web_actions": [] if actions_sent else web_actions,  # Don't send actions again
                    "intent": intent if i == len(words) - 1 else None,
                    "suggested_artworks": artwork_names if i == len(words) - 1 else [],
                    "full_response": response_text if i == len(words) - 1 else None
                }
                yield chunk_data
                
        except Exception as e:
            error_response = f"I'm having a bit of trouble right now. Let me try to help you directly! {str(e)}"
            yield {
                "chunk": error_response,
                "is_complete": True,
                "web_actions": [],
                "intent": "general_info",
                "suggested_artworks": [],
                "full_response": error_response
            }
    
    def _process_message_sync(self, user_message: str) -> ArtworkSuggestion:
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
        web_actions = []
        
        if intent in ["art_suggestion", "both"]:
            artwork_names = self._extract_suggested_artworks(response_text)
        
        # Build web actions from intermediate tool steps first (reliable)
        steps = result.get("intermediate_steps", [])
        web_actions = self._actions_from_steps(steps)
        
        # Fallback: also parse any explicit markers in the text
        if not web_actions:
            web_actions = self._parse_web_actions(response_text)
        
        # Add default search action ONLY when it's a pure suggestion (no imperative UI actions)
        has_imperative = any(a.get("type") in ["add_to_cart", "quick_view", "navigate", "checkout"] for a in web_actions)
        if not has_imperative and artwork_names and intent in ["art_suggestion", "both"]:
            search_string = " ".join(artwork_names).lower()
            if not any(action.get("type") == "search" for action in web_actions):
                web_actions.append({"type": "search", "value": search_string})
                web_actions.append({"type": "scroll", "value": "art-collection"})
        
        return ArtworkSuggestion(
            names=artwork_names,
            intent=intent,
            response=response_text,
            web_actions=web_actions
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
    
    def _parse_web_actions(self, response_text: str) -> List[Dict[str, str]]:
        """Parse web actions from agent response"""
        actions = []
        
        print(f"[DEBUG] Parsing web actions from text: {response_text}")
        
        # Robust regex-based extraction for markers if present
        markers = [
            (r"QUICK_VIEW:([^\n.!?]+)", "quick_view"),
            (r"ADD_TO_CART:([^\n.!?]+)", "add_to_cart"),
        ]
        for pattern, a_type in markers:
            try:
                m = re.search(pattern, response_text)
                if m:
                    name = m.group(1).strip()
                    actions.append({"type": a_type, "value": name})
                    print(f"[DEBUG] Added {a_type} action from text: {name}")
            except Exception as e:
                print(f"[DEBUG] Regex parse error for {a_type}: {e}")

        if "GO_TO_CART" in response_text:
            actions.append({"type": "navigate", "value": "cart"})
        if "GO_TO_HOME" in response_text:
            actions.append({"type": "navigate", "value": "home"})
        if "PROCEED_TO_CHECKOUT" in response_text:
            actions.append({"type": "checkout", "value": "start"})

        print(f"[DEBUG] Final actions from text: {actions}")
        return actions

    def _actions_from_steps(self, steps: List[Any]) -> List[Dict[str, str]]:
        """Build web actions from intermediate tool steps returned by the agent."""
        actions: List[Dict[str, str]] = []
        try:
            for step in steps:
                action = step[0] if isinstance(step, (list, tuple)) else step
                tool_name = getattr(action, "tool", "")
                tool_input = getattr(action, "tool_input", {})
                if isinstance(tool_input, str):
                    # Sometimes tool_input may be a plain string
                    parsed_input = {"text": tool_input}
                else:
                    parsed_input = dict(tool_input)

                if tool_name in ("quick_view", "quick_view_artwork"):
                    name = parsed_input.get("artwork_name") or parsed_input.get("text") or ""
                    if name:
                        actions.append({"type": "quick_view", "value": name})
                elif tool_name == "add_to_cart":
                    name = parsed_input.get("artwork_name") or parsed_input.get("text") or ""
                    if name:
                        actions.append({"type": "add_to_cart", "value": name})
                elif tool_name in ("navigate",):
                    dest = parsed_input.get("destination") or parsed_input.get("text")
                    if dest in {"cart", "home"}:
                        actions.append({"type": "navigate", "value": dest})
                elif tool_name in ("go_to_cart",):
                    actions.append({"type": "navigate", "value": "cart"})
                elif tool_name in ("go_to_home",):
                    actions.append({"type": "navigate", "value": "home"})
                elif tool_name in ("proceed_to_checkout", "checkout"):
                    actions.append({"type": "checkout", "value": "start"})
        except Exception as e:
            print(f"[DEBUG] Error building actions from steps: {e}")
        return actions
