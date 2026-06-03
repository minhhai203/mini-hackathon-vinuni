"""Default chat node placeholder."""

from src.agents.state import AgentState


def chat_node(state: AgentState) -> AgentState:
    return {**state, "answer": "Chat node is not implemented yet."}
