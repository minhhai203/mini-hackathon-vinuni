"""Agent graph assembly.

This file is the future home for LangGraph nodes and edges.
"""

from src.agents.state import AgentState
from src.agents.tools import AGENT_TOOLS


def run_agent(user_input: str) -> AgentState:
    available_tools = ", ".join(sorted(AGENT_TOOLS))
    return {
        "user_input": user_input,
        "answer": f"Agent graph is not implemented yet. Available tools: {available_tools}.",
    }
