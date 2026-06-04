from pathlib import Path

from src.agents.tools import AGENT_TOOLS
from src.agents.tools.evaluation import save_prompt_test_case, score_agent_response
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
    update_trip_profile,
    validate_user_constraints,
)


def test_search_vinpearl_pages_returns_official_candidates_only():
    result = search_vinpearl_pages("resort cho gia đình", destination="Phú Quốc")

    assert result["candidate_urls"]
    assert all("vinpearl.com" in url for url in result["candidate_urls"])
    assert result["next_tool"] == "crawl_vinpearl_page"
    assert result["needs_verification"] is True


def test_extract_resort_info_and_policy_guard():
    markdown = """
    # Vinpearl Resort Phú Quốc
    Khu nghỉ dưỡng biển có bãi biển riêng, hồ bơi, VinWonders và hoạt động cho trẻ em.
    Điều kiện voucher và phụ thu trẻ em cần kiểm tra theo từng gói.
    Chính sách hủy/hoàn tiền phụ thuộc rate plan.
    """

    resort = extract_resort_info(markdown, source_url="https://vinpearl.com/vi/phu-quoc")
    policy = extract_policy_guard(markdown)

    assert resort["name"] == "Vinpearl Resort Phú Quốc"
    assert "Phu Quoc" in resort["destinations"]
    assert "kids" in resort["amenities"]
    assert policy["confidence"] == "high"
    assert "voucher_membership" in policy["policy_items"]


def test_validate_followup_and_realtime_risk():
    profile = {
        "destination": "",
        "dates": "",
        "group": "2 người lớn 1 trẻ em",
        "budget": "800k/đêm",
        "priority": "villa riêng hồ bơi premium",
    }

    validation = validate_user_constraints(profile)
    questions = generate_followup_questions(profile)
    risk = detect_realtime_claim_risk("Voucher dùng được chắc chắn và còn phòng tối nay không?")

    assert validation["can_rank"] is False
    assert validation["contradictions"]
    assert questions
    assert risk["risk_level"] == "high"
    assert "voucher_code" in risk["missing_context"]


def test_rank_format_and_compare_recommendations():
    profile = {
        "destination": "Phu Quoc",
        "dates": "3 ngày 2 đêm",
        "group": "family with children",
        "budget": "15-20 triệu",
        "priority": "vui chơi cho trẻ em và nghỉ biển",
    }
    options = [
        {
            "name": "Vinpearl Phu Quoc Family Package",
            "destinations": ["Phu Quoc"],
            "amenities": ["kids", "theme_park", "beach"],
            "best_for": ["family_with_children"],
            "confidence": "medium",
        },
        {
            "name": "Vinpearl Nha Trang Spa Stay",
            "destinations": ["Nha Trang"],
            "amenities": ["spa", "pool"],
            "confidence": "medium",
        },
    ]

    ranked = rank_resort_options(profile, options)
    card = format_recommendation_card(ranked["shortlist"][0])
    diff = compare_previous_recommendations(options, ranked["shortlist"])

    assert ranked["confidence"] == "high"
    assert ranked["shortlist"][0]["name"] == "Vinpearl Phu Quoc Family Package"
    assert card["option"] == "Vinpearl Phu Quoc Family Package"
    assert diff["summary"]["removed_count"] == 1


def test_update_trip_profile_and_eval_helpers(tmp_path: Path):
    updated = update_trip_profile(
        {"destination": "Phu Quoc", "priority": "vui chơi"},
        {"destination": "Nha Trang", "priority": "nghỉ dưỡng nhẹ"},
    )
    saved = save_prompt_test_case("happy", "hello", {"answer": "ok"}, path=tmp_path / "cases.jsonl")
    score = score_agent_response(
        {"destination": "Nha Trang"},
        {
            "destination": "Nha Trang",
            "trade_off": "restriction cần kiểm tra",
            "policy_guard": "voucher, cancellation, phụ thu",
            "confidence": "medium",
            "next_step": "kiểm tra trên MyVinpearl",
        },
    )

    assert updated["needs_rerank"] is True
    assert updated["changed_fields"]["destination"]["new"] == "Nha Trang"
    assert saved["saved"] is True
    assert score["passed"] is True


def test_agent_tools_registry_contains_project_tools():
    expected = {
        "search_vinpearl_pages",
        "crawl_vinpearl_page",
        "load_cached_vinpearl_pages",
        "extract_resort_info",
        "extract_policy_guard",
        "validate_user_constraints",
        "rank_resort_options",
        "format_recommendation_card",
        "score_agent_response",
        "get_mock_weather_context",
        "get_mock_news_context",
        "get_mock_review_signals",
    }

    assert expected.issubset(AGENT_TOOLS)
