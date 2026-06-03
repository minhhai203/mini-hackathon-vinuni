"""Agent graph assembly.

This file is the future home for LangGraph nodes and edges.
"""

from src.agents.state import AgentState


def run_agent(user_input: str) -> AgentState:
    return {"user_input": user_input, "answer": "Agent graph is not implemented yet."}
