"""
AI Art Agent using LangChain for intelligent art search and recommendation
This agent can analyze user queries, search the art database, and perform web actions
"""

import json
import re
from typing import List, Dict, Any, Optional
from langchain_community.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from prompts import AGENT_PROMPT_TEMPLATE
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SearchArtTool(BaseTool):
    """Tool for searching art pieces by various criteria"""
    name: str = "search_art"
    description: str = "Search for art pieces by name, description, origin, or price range. Use keywords like 'japanese', 'abstract', 'landscape', country names, etc."
    
    def _run(self, query: str) -> str:
        """Search art database based on query.

        Note: expects ART_DATA to be provided by the runtime (e.g., imported
        or injected). This file focuses on the agent behavior rather than
        data loading.
        """
        query_lower = query.lower()
        matching_art = []
        
        for art in ART_DATA:
            # Search in name, description, and origin
            if (query_lower in art["name"].lower() or 
                query_lower in art["description"].lower() or 
                query_lower in art["origin"].lower()):
                matching_art.append(art)
        
        # Format results for the agent
        if not matching_art:
            return f"No art pieces found matching '{query}'"
        
        result = f"Found {len(matching_art)} art pieces matching '{query}':\n\n"
        for art in matching_art[:5]:  # Limit to top 5 results
            result += f"• {art['name']} - ${art['price']} (Origin: {art['origin']})\n"
            result += f"  Description: {art['description']}\n\n"
        
        return result
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)

class WebActionTool(BaseTool):
    """Tool for performing web actions like searching and scrolling"""
    name: str = "web_action"
    description: str = "Perform web actions: 'search:keyword' to search in searchbar, 'scroll:direction' to scroll page"
    
    def _run(self, action: str) -> str:
        """Execute web action"""
        if action.startswith("search:"):
            keyword = action.replace("search:", "").strip()
            # This would trigger the frontend search
            return f"SEARCH_ACTION:{keyword}"
        elif action.startswith("scroll:"):
            direction = action.replace("scroll:", "").strip()
            # This would trigger frontend scrolling
            return f"SCROLL_ACTION:{direction}"
        else:
            return "Invalid action. Use 'search:keyword' or 'scroll:direction'"
    
    async def _arun(self, action: str) -> str:
        """Async version"""
        return self._run(action)

class ArtRecommendationTool(BaseTool):
    """Tool for making personalized art recommendations"""
    name: str = "recommend_art"
    description: str = "Get personalized art recommendations based on user preferences like style, origin, price range, or themes"
    
        def _run(self, preferences: str) -> str:
            """Generate recommendations based on preferences.

            This is a simple score-based recommender over ART_DATA.
            """
        prefs_lower = preferences.lower()
        recommended = []
        
        # Smart matching based on preferences
        for art in ART_DATA:
            score = 0
            
            # Origin matching
            if any(country in prefs_lower for country in ["japan", "japanese"]):
                if art["origin"].lower() in ["japan", "korea", "china", "vietnam"]:
                    score += 3
            elif any(country in prefs_lower for country in ["european", "europe"]):
                if art["origin"].lower() in ["netherlands", "italy", "france", "spain"]:
                    score += 3
            
            # Style/theme matching
            if any(theme in prefs_lower for theme in ["abstract", "modern"]):
                if any(word in art["description"].lower() for word in ["abstract", "geometric", "bold"]):
                    score += 2
            elif any(theme in prefs_lower for theme in ["nature", "landscape"]):
                if any(word in art["description"].lower() for word in ["forest", "river", "mountain", "flowers"]):
                    score += 2
            elif any(theme in prefs_lower for theme in ["peaceful", "calm", "tranquil"]):
                if any(word in art["description"].lower() for word in ["tranquil", "peaceful", "calm", "gentle"]):
                    score += 2
            
            # Price range matching
            if "affordable" in prefs_lower or "budget" in prefs_lower:
                if art["price"] < 2000:
                    score += 1
            elif "premium" in prefs_lower or "luxury" in prefs_lower:
                if art["price"] > 2500:
                    score += 1
            
            if score > 0:
                recommended.append((art, score))
        
        # Sort by score and get top recommendations
        recommended.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = recommended[:3]
        
        if not top_recommendations:
            return "I couldn't find specific recommendations based on your preferences. Let me search our general collection."
        
        result = f"Based on your preferences, I recommend these artworks:\n\n"
        for art, score in top_recommendations:
            result += f"🎨 {art['name']} - ${art['price']}\n"
            result += f"   Origin: {art['origin']}\n"
            result += f"   {art['description']}\n\n"
        
        return result
    
    async def _arun(self, preferences: str) -> str:
        """Async version"""
        return self._run(preferences)

class ArtAgent:
    """Main Art Agent class that orchestrates the AI assistant"""
    
    def __init__(self, openai_api_key: str):
        self.llm = OpenAI(
            temperature=0.7,
            openai_api_key=openai_api_key,
            max_tokens=500
        )
        
        # Initialize tools
        self.tools = [
            SearchArtTool(),
            WebActionTool(), 
            ArtRecommendationTool()
        ]
        
        # Create agent prompt from centralized template
        self.prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "chat_history"],
            template=AGENT_PROMPT_TEMPLATE,
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3
        )
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and return response with any web actions"""
        try:
            # Run the agent
            response = self.agent_executor.run(input=user_message)
            
            # Extract any web actions from the response
            web_actions = []
            if "SEARCH_ACTION:" in response:
                search_terms = re.findall(r"SEARCH_ACTION:([^\n]+)", response)
                for term in search_terms:
                    web_actions.append({"type": "search", "value": term.strip()})
            
            if "SCROLL_ACTION:" in response:
                scroll_commands = re.findall(r"SCROLL_ACTION:([^\n]+)", response)
                for command in scroll_commands:
                    web_actions.append({"type": "scroll", "value": command.strip()})
            
            # Clean response of action commands
            clean_response = re.sub(r"SEARCH_ACTION:[^\n]+", "", response)
            clean_response = re.sub(r"SCROLL_ACTION:[^\n]+", "", clean_response)
            clean_response = clean_response.strip()
            
            return {
                "response": clean_response,
                "web_actions": web_actions,
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while processing your request. Let me try to help you differently. What specific type of art are you looking for?",
                "web_actions": [],
                "success": False,
                "error": str(e)
            }
    
    def get_art_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get art suggestions based on query for frontend display"""
        query_lower = query.lower()
        suggestions = []
        
        for art in ART_DATA:
            if (query_lower in art["name"].lower() or 
                query_lower in art["description"].lower() or 
                query_lower in art["origin"].lower()):
                suggestions.append(art)
        
        return suggestions[:6]  # Return top 6 for display

# Example usage and testing
if __name__ == "__main__":
    # This would be initialized with actual OpenAI API key
    # agent = ArtAgent(openai_api_key="your-openai-key-here")
    
    # Test without actual LLM
    print("Art Agent initialized successfully!")
    print("\nAvailable art pieces (sample):")
    for art in ART_DATA[:3]:
        print(f"- {art['name']} ({art['origin']}) - ${art['price']}")
