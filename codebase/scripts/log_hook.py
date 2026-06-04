#!/usr/bin/env python3
"""Append an AI tool interaction log from environment variables or stdin."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path(".ai-log")


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": os.getenv("AI_TOOL", "unknown"),
        "event": os.getenv("AI_EVENT", "prompt"),
        "content": sys.stdin.read().strip(),
    }
    with (LOG_DIR / "ai-usage.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
