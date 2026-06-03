#!/usr/bin/env python3
"""Manual logger for web AI tools such as ChatGPT."""

from __future__ import annotations

import argparse
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("content", help="Prompt or response content to log")
    args = parser.parse_args()
    subprocess.run(
        ["python", "scripts/log_hook.py"],
        input=args.content,
        text=True,
        check=False,
    )


if __name__ == "__main__":
    main()
