"""Shared text helpers for agent tools."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str) -> str:
    """Lowercase text and remove accents for keyword matching."""
    normalized = unicodedata.normalize("NFD", value or "")
    without_accents = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", without_accents.lower()).strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(keyword) in normalized for keyword in keywords)


def first_matching_lines(text: str, keywords: list[str], *, limit: int = 3) -> list[str]:
    matches: list[str] = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip(" -#\t")
        if line and contains_any(line, keywords):
            matches.append(line)
        if len(matches) >= limit:
            break
    return matches
