#!/usr/bin/env python3
"""Print AI usage log summary for submission hooks."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    log_file = Path(".ai-log/ai-usage.jsonl")
    if not log_file.exists():
        print("No AI usage log found.")
        return

    lines = log_file.read_text(encoding="utf-8").splitlines()
    print(f"AI usage log entries: {len(lines)}")


if __name__ == "__main__":
    main()
