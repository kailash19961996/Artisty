"""
ARTISTY BACKEND UTILS - AI ASSISTANT FOR ART GALLERY

This module provides an AI assistant for the Artisty art gallery application.
Features intelligent artwork recommendations, contextual search, and UI control
through structured tool calls and direct action mapping.
"""

import os
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


@dataclass
class ArtworkSuggestion:
    names: List[str]
    intent: str
    response: str
    web_actions: List[Dict[str, str]]


class ArtistryAssistant:
    """AI-powered gallery assistant with contextual search and UI control"""
    
    def __init__(self, inventory_text: str, model_name: str = "gpt-4o-mini"):
        self.inventory_text = inventory_text
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self._last_search_artworks = []  # Store extracted artwork names from search
        # Parse inventory names for validation and anti-hallucination
        self.inventory_names = self._parse_inventory_names(inventory_text)
        # Build structured index for enhanced search capabilities
        self.inventory_index = self._build_inventory_index(inventory_text)
        # Track recommendation history for diversity
        self.recommended_history: List[str] = []
        
        # Conversation memory for context awareness
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000
        )
        
        # Initialize tools and agent
        self.tools = self._create_tools()
        self.planner_agent = self._create_planner_agent()
        self.planner_executor = AgentExecutor(
            agent=self.planner_agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=4,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def _create_tools(self):
        """Create tools with simple schemas"""
        
        class QuickViewInput(BaseModel):
            artwork_name: str = Field(..., description="Exact artwork name to open in quick view")

        class AddToCartInput(BaseModel):
            artwork_name: str = Field(..., description="Exact artwork name to add to cart")

        class NavigateInput(BaseModel):
            destination: str = Field(..., description="Destination to navigate to: 'cart' or 'home'")

        class SearchInput(BaseModel):
            query: str = Field(..., description="Search query for artworks")

        class CheckoutInput(BaseModel):
            """Empty schema for proceeding to checkout"""
            pass

        return [
            StructuredTool.from_function(
                name="search_inventory",
                description="Search artworks by criteria",
                func=self._search_inventory_tool,
                args_schema=SearchInput,
            ),
            StructuredTool.from_function(
                name="quick_view",
                description="Open artwork popup",
                func=self._quick_view_artwork_tool,
                args_schema=QuickViewInput,
            ),
            StructuredTool.from_function(
                name="add_to_cart",
                description="Add artwork to cart",
                func=self._add_to_cart_tool,
                args_schema=AddToCartInput,
            ),
            StructuredTool.from_function(
                name="navigate",
                description="Navigate to page",
                func=self._navigate_tool,
                args_schema=NavigateInput,
            ),
            StructuredTool.from_function(
                name="checkout",
                description="Proceed to checkout in the cart",
                func=self._checkout_tool,
                args_schema=CheckoutInput,
            ),
        ]

    def _create_planner_agent(self):
        """Create the main planning agent with tool routing capabilities"""
        
        planner_prompt = f"""You are the Planner for the Artisty gallery assistant.

        POLICY:
        - Maintain conversation and answer general questions yourself. Do NOT call a tool for general chit-chat or policy questions.
        - Only call a tool when the USER'S INTENT REQUIRES IT.
        - For recommendations of artworks, call ONLY the tool: search_inventory.
        - Do NOT call quick_view or add_to_cart unless the user explicitly asks to open/view a specific named artwork or add one to the cart.
        - When you call search_inventory, provide a succinct natural-language response to the user in your final message. The search tool will also provide a list of validated artwork names which the UI will use. Your text must be consistent with the tool results.
        - Do not hallucinate artwork names.

        TOOLS AVAILABLE:
        - search_inventory(query): Contextual art recommender that reads the full inventory with conversation context and returns JSON (response text + validated artwork names). Use when user asks for suggestions, alternatives, or themed artworks.
        - quick_view(artwork_name): Open artwork popup (ONLY if user explicitly says to open/view a specific artwork by exact name)
        - add_to_cart(artwork_name): Add artwork to cart (ONLY if user explicitly asks to add/buy)
        - navigate(destination): Navigate to cart or home (ONLY if user explicitly asks to go to cart/checkout/home)
        - checkout(): Proceed to checkout (ONLY if user asks to checkout / pay / proceed)

        EXAMPLES:
        - "open Voltage Dreams" → quick_view(artwork_name="Voltage Dreams")
        - "add Voltage Dreams to cart" → add_to_cart(artwork_name="Voltage Dreams")
        - "go to cart" → navigate(destination="cart")
        - "proceed to checkout" → checkout()
        - "show me blue art" → search_inventory(query="blue")

        Remember: If the user is NOT asking for recommendations, simply reply in conversation without using tools. If the user asks for recommendations, call search_inventory with their request (and the memory context will be included by the tool)."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", planner_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)

    def _parse_inventory_names(self, inventory_text: str) -> List[str]:
        """Extract canonical artwork names from the inventory text.
        Expected line format examples:
          '1. Chrome Velocity - $2900.0 (Netherlands) - ...'
        Returns a list of names like ['Chrome Velocity', ...]
        """
        names: List[str] = []
        try:
            import re
            for line in inventory_text.splitlines():
                m = re.match(r"\s*\d+\.\s*([^\-\n]+?)\s*-", line)
                if m:
                    name = m.group(1).strip()
                    if name:
                        names.append(name)
        except Exception as _:
            pass
        return names

    def _build_inventory_index(self, inventory_text: str) -> Dict[str, Dict[str, Any]]:
        """Lightweight parsing of inventory into structured fields for grounding.
        Returns dict[name] = { country, price, raw }
        """
        import re
        index: Dict[str, Dict[str, Any]] = {}
        for line in inventory_text.splitlines():
            m = re.match(r"\s*\d+\.\s*([^\-\n]+?)\s*-\s*\$(\d+\.?\d*)\s*\(([^\)]+)\)\s*-\s*(.*)$", line)
            if m:
                name = m.group(1).strip()
                price = float(m.group(2)) if m.group(2) else None
                country = m.group(3).strip()
                raw = m.group(4).strip()
                index[name] = {"country": country, "price": price, "raw": raw}
        return index



    def _search_inventory_tool(self, query: str) -> str:
        """LLM-powered contextual search with anti-hallucination validation"""
        # Extract recent conversation context for personalized recommendations
        try:
            recent_msgs = getattr(self.memory, "chat_memory").messages[-10:]
            context_text = "\n".join([getattr(m, "content", "") for m in recent_msgs if getattr(m, "content", "")])
        except Exception:
            context_text = ""

        names_block = "\n".join(self.inventory_names)
        history_block = ", ".join(self.recommended_history[-5:]) if self.recommended_history else ""

        search_prompt = f"""You are an art gallery store assistant. A user is asking: "{query}"

        CONVERSATION CONTEXT (most recent):
        {context_text}

        DIVERSITY PREFERENCE (soft): Previously recommended artworks in this session (prefer showing different ones next):
        {history_block}

        COMPLETE INVENTORY (full details):
        {self.inventory_text}

        INVENTORY NAMES (canonical, exact spellings):
        {names_block}

        Your task (behave like a thoughtful store assistant):
        1. Prioritize the user's current request first. Treat CONVERSATION CONTEXT as OPTIONAL: use it if it helps, ignore it if it conflicts with the current request.
        2. Detect explicit constraints (e.g., country like "from USA", color, theme like "adventurous", budget). 
        3. If EXACT matches exist, recommend them. If NO exact matches exist, you have two options:
           a) If there are CLOSE alternatives (e.g., user asks "Eastern Europe" but we have Poland/Ukraine/Russia), recommend those close alternatives and explain the connection
           b) If NO close alternatives exist, return empty artworks array and explain what we don't have, then suggest what we DO have that might interest them
        4. Provide a concise, helpful response. If you recommend artworks, reference only those you will list in the 'artworks' array.
        5. List the relevant artwork names clearly. IMPORTANT: names must be EXACTLY as they appear in the inventory (see INVENTORY NAMES). Do not invent or rename.
        6. Prefer diversity across turns: if the user asked to "show something else", choose different items than the earlier list when reasonable.

        EXAMPLES:
        - User asks "Eastern Europe" → We have Poland, Ukraine, Russia → Recommend those and explain "I found artworks from Eastern European countries like Poland, Ukraine, and Russia"
        - User asks "purple themes" → We have several purple artworks → Recommend them
        - User asks "sculptures" → We only have paintings → Return empty array and explain "We specialize in paintings, but here are some dynamic pieces that might interest you"

        Return your response as valid JSON in this exact format:
        {{
            "response": "Your helpful explanation of what you found or close alternatives",
            "artworks": ["Artwork Name 1", "Artwork Name 2", "Artwork Name 3"],
            "count": 3
        }}

        Return up to 6 most relevant artworks. If no artworks match and no close alternatives exist, return an empty array for artworks and explain what we don't have."""

        try:
            # Use structured JSON mode for reliable response parsing
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="You are an art gallery assistant. Always respond with valid JSON."),
                HumanMessage(content=search_prompt)
            ]
            
            # Attempt JSON mode, fallback to regular mode if unavailable
            try:
                result = self.llm.invoke(
                    messages,
                    response_format={"type": "json_object"}
                )
                response_text = result.content.strip()
            except Exception as json_mode_error:
                print(f"JSON mode unavailable, using regular mode: {json_mode_error}")
                result = self.llm.invoke(search_prompt)
                response_text = result.content.strip()
            
            print(f"[DEBUG] Raw LLM response: {response_text}")
            
            # Try to parse as JSON first
            try:
                parsed_response = json.loads(response_text)
                
                # Extract structured data
                response_part = parsed_response.get("response", "")
                artwork_names = parsed_response.get("artworks", [])
                count = parsed_response.get("count", len(artwork_names))
                
                # Validate and clean artwork names
                if isinstance(artwork_names, list):
                    artwork_names = [name.strip() for name in artwork_names if name and name.strip()]
                elif isinstance(artwork_names, str):
                    # Handle case where artworks is returned as comma-separated string
                    artwork_names = [name.strip() for name in artwork_names.split(',') if name.strip()]
                else:
                    artwork_names = []
                
                # Validate artwork names against inventory to prevent hallucination
                artwork_names = [n for n in artwork_names if n in self.inventory_names]
                
                print(f"JSON parsed successfully - Found {len(artwork_names)} artworks: {artwork_names}")
                
                # Ensure response accuracy when no artworks found
                if len(artwork_names) == 0:
                    lowered = (response_part or "").lower()
                    if not any(kw in lowered for kw in ["no ", "couldn't", "cannot", "didn't find", "don't have"]):
                        response_part = (
                            f"I couldn't find any specific artworks related to {query} in our inventory. "
                            "Would you like to explore some alternatives?"
                        )
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing failed: {json_error}")
                response_part = (
                    "I'm sorry — I couldn't produce a structured recommendation just now. "
                    "Please rephrase your request or try again."
                )
                artwork_names = []
            
            # Ensure response is available
            if not response_part:
                response_part = "I found some artworks that might interest you."
            
            # Store validated artwork names for frontend actions
            self._last_search_artworks = artwork_names[:6]
            # Update recommendation history for diversity tracking
            for n in self._last_search_artworks:
                if n not in self.recommended_history:
                    self.recommended_history.append(n)
            if len(self.recommended_history) > 50:
                self.recommended_history = self.recommended_history[-50:]
            
            print(f"Search result - Response: '{response_part[:120]}...', Artworks: {self._last_search_artworks}")
            return response_part
            
        except Exception as e:
            print(f"Search tool error: {str(e)}")
            self._last_search_artworks = []
            return f"I'm having trouble searching right now. Please try again. (Error: {str(e)})"

    def _quick_view_artwork_tool(self, artwork_name: str) -> str:
        """Quick view tool"""
        return f"Opening quick view for {artwork_name}."

    def _add_to_cart_tool(self, artwork_name: str) -> str:
        """Add to cart tool"""
        return f"Adding {artwork_name} to cart."

    def _navigate_tool(self, destination: str) -> str:
        """Navigate tool"""
        return f"Navigating to {destination}."

    def _checkout_tool(self) -> str:
        """Proceed to checkout tool"""
        return "Proceeding to checkout."

    def process_message(self, user_message: str) -> ArtworkSuggestion:
        """Process user message and generate response with web actions"""
        try:
            print(f"Processing: {user_message}")
            
            # Execute planning agent
            planner_result = self.planner_executor.invoke({"input": user_message})
            
            planner_output = planner_result.get("output", "")
            tool_steps = planner_result.get("intermediate_steps", [])
            
            print(f"Planner output: {planner_output}")
            print(f"Tool steps: {len(tool_steps)}")
            
            # Map tool calls to web actions
            web_actions = []
            
            for step in tool_steps:
                if isinstance(step, (list, tuple)) and len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_name = getattr(action, "tool", "unknown")
                    tool_input = getattr(action, "tool_input", {})
                    
                    print(f"Tool: {tool_name}, Input: {tool_input}")
                    
                    if tool_name == "quick_view":
                        artwork_name = tool_input.get("artwork_name", "")
                        if artwork_name:
                            web_actions.append({"type": "quick_view", "value": artwork_name})
                            
                    elif tool_name == "add_to_cart":
                        artwork_name = tool_input.get("artwork_name", "")
                        if artwork_name:
                            web_actions.append({"type": "add_to_cart", "value": artwork_name})
                            
                    elif tool_name == "navigate":
                        destination = tool_input.get("destination", "")
                        if destination:
                            web_actions.append({"type": "navigate", "value": destination})
                    
                    elif tool_name == "checkout":
                        web_actions.append({"type": "checkout"})
                            
                    elif tool_name == "search_inventory":
                        query = tool_input.get("query", "")
                        extracted_artworks = getattr(self, '_last_search_artworks', [])
                        
                        if extracted_artworks:
                            # Use specific artwork names for targeted search
                            search_term = " ".join(extracted_artworks)
                            print(f"Using artwork names for search: {search_term}")
                            print(f"Individual artworks: {extracted_artworks}")
                            
                            web_actions.extend([
                                {"type": "search", "value": search_term},
                                {"type": "scroll", "value": "art-collection"}
                            ])
                        else:
                            # No matches found, scroll to gallery without search
                            print(f"No artworks found for '{query}', showing gallery")
                            web_actions.append({"type": "scroll", "value": "art-collection"})
            
            print(f"Generated actions: {web_actions}")
            
            # Use search tool response for consistency when available
            if any(getattr(step[0], "tool", "") == "search_inventory" for step in tool_steps if isinstance(step, (list, tuple)) and len(step) >= 2):
                for step in reversed(tool_steps):
                    if isinstance(step, (list, tuple)) and len(step) >= 2 and getattr(step[0], "tool", "") == "search_inventory":
                        planner_output = step[1]
                        break

            response_text = planner_output or "I'd be happy to help you!"
            intent = "art_suggestion" if any("search" in action["type"] for action in web_actions) else "general_info"
            extracted_artworks = getattr(self, '_last_search_artworks', [])
            
            return ArtworkSuggestion(
                names=extracted_artworks,
                intent=intent,
                response=response_text,
                web_actions=web_actions
            )
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return ArtworkSuggestion(
                names=[],
                intent="general_info",
                response=f"I encountered an error: {str(e)}",
                web_actions=[]
            )


def create_assistant(openai_api_key: str, model_name: str = "gpt-4o-mini") -> ArtistryAssistant:
    """Create and initialize the Artisty AI assistant"""
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Load artwork inventory from file
    inventory_path = "/opt/art.txt"
    if not os.path.exists(inventory_path):
        inventory_path = "art.txt"
    
    try:
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory_text = f.read().strip()
    except Exception as e:
        print(f"Error loading inventory: {e}")
        inventory_text = "No inventory available"
    
    return ArtistryAssistant(inventory_text, model_name)
