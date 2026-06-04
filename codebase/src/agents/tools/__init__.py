"""Agent tools."""

from src.agents.tools.context import get_mock_news_context, get_mock_review_signals, get_mock_weather_context
from src.agents.tools.evaluation import save_prompt_test_case, score_agent_response
from src.agents.tools.example import example_tool
from src.agents.tools.extraction import extract_policy_guard, extract_resort_info
from src.agents.tools.recommendation import (
    compare_previous_recommendations,
    format_recommendation_card,
    rank_resort_options,
)
from src.agents.tools.source_discovery import search_vinpearl_pages
from src.agents.tools.trip_planning import (
    detect_realtime_claim_risk,
    generate_followup_questions,
    handoff_to_human,
    update_trip_profile,
    validate_user_constraints,
)
from src.agents.tools.vinpearl_crawler import (
    crawl_and_cache_vinpearl_page_sync,
    crawl_vinpearl_page,
    crawl_vinpearl_page_sync,
    load_cached_vinpearl_page,
    load_cached_vinpearl_pages,
    normalize_vinpearl_url,
    save_crawled_vinpearl_page,
    vinpearl_cache_path,
)


AGENT_TOOLS = {
    "example_tool": example_tool,
    "search_vinpearl_pages": search_vinpearl_pages,
    "crawl_vinpearl_page": crawl_vinpearl_page,
    "crawl_vinpearl_page_sync": crawl_vinpearl_page_sync,
    "crawl_and_cache_vinpearl_page_sync": crawl_and_cache_vinpearl_page_sync,
    "load_cached_vinpearl_page": load_cached_vinpearl_page,
    "load_cached_vinpearl_pages": load_cached_vinpearl_pages,
    "save_crawled_vinpearl_page": save_crawled_vinpearl_page,
    "get_mock_weather_context": get_mock_weather_context,
    "get_mock_news_context": get_mock_news_context,
    "get_mock_review_signals": get_mock_review_signals,
    "extract_resort_info": extract_resort_info,
    "extract_policy_guard": extract_policy_guard,
    "validate_user_constraints": validate_user_constraints,
    "detect_realtime_claim_risk": detect_realtime_claim_risk,
    "generate_followup_questions": generate_followup_questions,
    "update_trip_profile": update_trip_profile,
    "handoff_to_human": handoff_to_human,
    "rank_resort_options": rank_resort_options,
    "format_recommendation_card": format_recommendation_card,
    "compare_previous_recommendations": compare_previous_recommendations,
    "save_prompt_test_case": save_prompt_test_case,
    "score_agent_response": score_agent_response,
}


__all__ = [
    "AGENT_TOOLS",
    "compare_previous_recommendations",
    "crawl_vinpearl_page",
    "crawl_vinpearl_page_sync",
    "crawl_and_cache_vinpearl_page_sync",
    "detect_realtime_claim_risk",
    "extract_policy_guard",
    "extract_resort_info",
    "example_tool",
    "format_recommendation_card",
    "get_mock_news_context",
    "get_mock_review_signals",
    "get_mock_weather_context",
    "generate_followup_questions",
    "handoff_to_human",
    "normalize_vinpearl_url",
    "rank_resort_options",
    "save_prompt_test_case",
    "score_agent_response",
    "search_vinpearl_pages",
    "update_trip_profile",
    "validate_user_constraints",
    "load_cached_vinpearl_page",
    "load_cached_vinpearl_pages",
    "save_crawled_vinpearl_page",
    "vinpearl_cache_path",
]
