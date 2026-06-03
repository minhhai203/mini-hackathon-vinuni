"""Evaluation helpers for prompt tests and agent responses."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agents.tools.text_utils import contains_any, normalize_text


DEFAULT_EVAL_LOG = Path("eval/agent-test-cases.jsonl")


def save_prompt_test_case(
    case_name: str,
    user_input: str,
    agent_output: dict[str, Any] | str,
    *,
    path: str | Path = DEFAULT_EVAL_LOG,
) -> dict[str, Any]:
    """Append a prompt test case to the evaluation log."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_name": case_name,
        "user_input": user_input,
        "agent_output": agent_output,
    }
    with output_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"saved": True, "path": str(output_path), "case_name": case_name}


def score_agent_response(user_profile: dict[str, Any], agent_output: dict[str, Any] | str) -> dict[str, Any]:
    """Score an output against the prototype safety/relevance rubric."""
    output_text = json.dumps(agent_output, ensure_ascii=False) if isinstance(agent_output, dict) else str(agent_output)
    destination = str(user_profile.get("destination") or "")
    checks = {
        "mentions_destination": bool(destination and normalize_text(destination) in normalize_text(output_text)),
        "has_tradeoff": contains_any(output_text, ["trade-off", "tradeoff", "đánh đổi", "restriction", "hạn chế"]),
        "has_policy_guard": contains_any(output_text, ["policy", "cancellation", "voucher", "phụ thu", "hoàn tiền"]),
        "has_confidence": contains_any(output_text, ["confidence", "độ tin cậy", "low", "medium", "high"]),
        "has_next_action": contains_any(output_text, ["next", "kiểm tra", "cs kh", "cskh", "myvinpearl", "vinpearl"]),
    }
    score = sum(1 for passed in checks.values() if passed)
    return {
        "score": score,
        "max_score": len(checks),
        "checks": checks,
        "passed": score >= 4,
    }
