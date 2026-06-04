import json

from src.services.vinpearl_data import load_vinpearl_options_from_cache


def test_load_vinpearl_options_from_cache_converts_crawl_json(tmp_path):
    (tmp_path / "crawl-summary.json").write_text("[]", encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not-json", encoding="utf-8")
    (tmp_path / "vinpearl-phu-quoc.json").write_text(
        json.dumps(
            {
                "requested_url": "https://vinpearl.com/vi/phu-quoc",
                "success": True,
                "title": "Vinpearl Phu Quoc",
                "markdown": (
                    "# Vinpearl Resort Phú Quốc\n"
                    "Resort biển có bãi biển, hồ bơi, VinWonders, nhà hàng và hoạt động cho trẻ em. "
                    "Điều kiện voucher và phụ thu trẻ em cần kiểm tra theo từng gói."
                ),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    options = load_vinpearl_options_from_cache(tmp_path)

    assert len(options) == 1
    assert options[0]["name"] == "Vinpearl Resort Phú Quốc"
    assert options[0]["data_source"] == "vinpearl_crawl_cache"
    assert options[0]["source_url"] == "https://vinpearl.com/vi/phu-quoc"
    assert "Phu Quoc" in options[0]["destinations"]
    assert "kids" in options[0]["amenities"]
    assert options[0]["context_badges"][0] == "Official crawl"
    assert options[0]["policy_guard"]["policy_items"]


def test_load_vinpearl_options_from_cache_returns_empty_when_missing(tmp_path):
    missing_dir = tmp_path / "missing"

    assert load_vinpearl_options_from_cache(missing_dir) == []


def test_load_vinpearl_options_prefers_structured_catalog_fields(tmp_path):
    (tmp_path / "catalog-index.json").write_text("{}", encoding="utf-8")
    (tmp_path / "catalog-phu-quoc.json").write_text(
        json.dumps(
            {
                "requested_url": "https://vinpearl.com/vi/vinpearl-wonderworld-phu-quoc",
                "success": True,
                "source": "official_vinpearl_catalog_enriched",
                "markdown": "# Noisy page text",
                "structured": {
                    "name": "Vinpearl Wonderworld Phú Quốc",
                    "option_type": "stay",
                    "destinations": ["Phu Quoc"],
                    "amenities": ["villa", "pool", "kids", "theme_park"],
                    "best_for": ["family_with_children"],
                    "context_badges": ["Official menu", "Stay", "Phu Quoc"],
                    "image_url": "assets/destination-phuquoc.png",
                    "confidence": "high",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    options = load_vinpearl_options_from_cache(tmp_path)

    assert len(options) == 1
    assert options[0]["name"] == "Vinpearl Wonderworld Phú Quốc"
    assert options[0]["data_source"] == "official_vinpearl_catalog_enriched"
    assert options[0]["confidence"] == "high"
    assert "theme_park" in options[0]["amenities"]
    assert options[0]["context_badges"] == ["Official menu", "Stay", "Phu Quoc"]
