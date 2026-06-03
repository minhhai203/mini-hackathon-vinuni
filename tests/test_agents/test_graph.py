from src.agents.graph import run_agent


def test_run_agent_returns_state():
    state = run_agent("hello")

    assert state["user_input"] == "hello"
    assert "answer" in state
