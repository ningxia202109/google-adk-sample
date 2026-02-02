import httpx
import json
import os
from typing import List, Optional, Any
from google.adk.tools import FunctionTool, BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.agents.readonly_context import ReadonlyContext

# Registry for skill discovery
from .agent_skill_registry import SkillRegistry

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
registry = SkillRegistry(SKILLS_DIR)

BASE_URL = "http://127.0.0.1:6060"

# --- API Tools for Users ---

async def get_users() -> str:
    """Fetch all users from the service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/users")
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error fetching users: {str(e)}"

async def create_user(name: str, email: str, habits: List[str] = []) -> str:
    """Create a new user.
    
    Args:
        name: The name of the user.
        email: The email of the user.
        habits: List of user habits.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {"name": name, "email": email, "habits": habits}
            response = await client.post(f"{BASE_URL}/users", json=payload)
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error creating user: {str(e)}"

async def update_user(user_id: int, name: Optional[str] = None, email: Optional[str] = None, habits: Optional[List[str]] = None) -> str:
    """Update an existing user.
    
    Args:
        user_id: The ID of the user to update.
        name: Updated name.
        email: Updated email.
        habits: Updated habits.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {}
            if name: payload["name"] = name
            if email: payload["email"] = email
            if habits is not None: payload["habits"] = habits
            response = await client.put(f"{BASE_URL}/users/{user_id}", json=payload)
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error updating user: {str(e)}"

# --- API Tools for Teams ---

async def get_teams() -> str:
    """Fetch all teams from the service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/teams")
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error fetching teams: {str(e)}"

async def add_user_to_team(team_name: str, user_id: int) -> str:
    """Add a user to a team.
    
    Args:
        team_name: The name of the team.
        user_id: The ID of the user to add.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/teams/{team_name}/users/{user_id}")
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error adding user to team: {str(e)}"

# --- Skill Management Tools ---

async def search_skills(query: str) -> str:
    """Search for relevant skills from the skill library.
    
    Args:
        query: User query or intent to match against skills.
    """
    results = registry.search_skills(query)
    if not results:
        return "No relevant skills found."
    return json.dumps([r.model_dump() for r in results], indent=2)

async def load_skill(skill_name: str, tool_context: Any) -> str:
    """Load a specific skill into the agent context.
    
    Args:
        skill_name: The name of the skill to load.
    """
    skill = registry.get_skill(skill_name)
    if not skill:
        return f"Skill '{skill_name}' not found."
    
    # Store the active skill name in the session state
    tool_context.state["active_skill"] = skill_name
    return f"Skill '{skill_name}' loaded successfully. I am now equipped with specialized instructions and tools for this task."

async def complete_skill(tool_context: Any) -> str:
    """Mark the current skill as completed and off-load it from context."""
    active_skill = tool_context.state.get("active_skill")
    if not active_skill:
        return "No skill is currently active."
    
    del tool_context.state["active_skill"]
    return f"Skill '{active_skill}' has been off-loaded. I have returned to my base state."

# --- Dynamic Toolset ---

class DynamicSkillToolset(BaseToolset):
    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> List[BaseTool]:
        tools = [
            FunctionTool(search_skills),
            FunctionTool(load_skill),
            FunctionTool(complete_skill)
        ]
        
        if not readonly_context:
            return tools

        active_skill_name = readonly_context.state.get("active_skill")
        if not active_skill_name:
            return tools

        # Add tools based on active skill
        if active_skill_name == "skill_register_user":
            tools.extend([
                FunctionTool(get_users),
                FunctionTool(create_user),
                FunctionTool(update_user)
            ])
        elif active_skill_name == "skill_assign_user_to_team":
            tools.extend([
                FunctionTool(get_users), # Often needed to find user_id
                FunctionTool(get_teams),
                FunctionTool(add_user_to_team)
            ])
            
        return tools
