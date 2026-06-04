#!/usr/bin/env python3
"""Scan Antigravity prompt files and append them to the AI usage log."""

from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    for prompt_file in Path(".agents").glob("**/*.md"):
        subprocess.run(
            ["python", "scripts/log_hook.py"],
            input=prompt_file.read_text(encoding="utf-8"),
            text=True,
            check=False,
        )


if __name__ == "__main__":
    main()
