"""Agent tools."""

from src.agents.tools.example import example_tool
from src.agents.tools.vinpearl_crawler import (
    crawl_vinpearl_page,
    crawl_vinpearl_page_sync,
    normalize_vinpearl_url,
)


AGENT_TOOLS = {
    "example_tool": example_tool,
    "crawl_vinpearl_page": crawl_vinpearl_page,
    "crawl_vinpearl_page_sync": crawl_vinpearl_page_sync,
}


__all__ = [
    "AGENT_TOOLS",
    "crawl_vinpearl_page",
    "crawl_vinpearl_page_sync",
    "example_tool",
    "normalize_vinpearl_url",
]
