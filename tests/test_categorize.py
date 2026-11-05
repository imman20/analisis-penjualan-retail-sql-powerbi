"""Pengujian pemetaan kategori produk berbasis kata kunci."""

from __future__ import annotations

import pandas as pd

from src.data.categorize import DEFAULT_CATEGORY, categorize_description, categorize_series


def test_keyword_rules_map_to_expected_categories():
    assert categorize_description("PAPER CHAIN KIT 50'S CHRISTMAS") == "Christmas & Seasonal"
    assert categorize_description("JUMBO BAG RED RETROSPOT") == "Bags & Accessories"
    assert categorize_description("WHITE HANGING HEART T-LIGHT HOLDER") == "Candles & Lighting"
    assert categorize_description("REGENCY CAKESTAND 3 TIER") == "Kitchen & Dining"
    assert categorize_description("ASSORTED COLOUR BIRD ORNAMENT") == "Garden & Outdoor"


def test_specific_rules_take_precedence_over_generic():
    # Mengandung "DECORATION" (Home Decor) tetapi juga "CHRISTMAS" yang lebih spesifik.
    assert categorize_description("CHRISTMAS TREE DECORATION") == "Christmas & Seasonal"


def test_unknown_and_missing_descriptions_fall_back_to_default():
    assert categorize_description("ZZZ UNKNOWN THING") == DEFAULT_CATEGORY
    assert categorize_description(None) == DEFAULT_CATEGORY
    assert categorize_description(float("nan")) == DEFAULT_CATEGORY


def test_categorize_series_is_case_insensitive_and_handles_na():
    series = pd.Series(["jumbo bag pink", None, "Rabbit Night Light"])
    result = categorize_series(series)
    assert list(result) == ["Bags & Accessories", DEFAULT_CATEGORY, "Candles & Lighting"]
