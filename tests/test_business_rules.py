import numpy as np
import pytest

from constants import SUGGESTED_FACTORS


def test_factor_selection_boundaries_reflect_current_implementation(app_module):
    assert len(SUGGESTED_FACTORS) == 7

    one_factor_pairs = app_module.build_pairs(["Cost"])
    minimum_valid_pairs = app_module.build_pairs(["Cost", "Speed"])
    maximum_available_pairs = app_module.build_pairs(SUGGESTED_FACTORS)

    assert one_factor_pairs == []
    assert len(minimum_valid_pairs) == 1
    assert len(maximum_available_pairs) == 21


def test_option_pair_boundaries_for_allowed_option_counts(app_module):
    two_options = ["Open Branch", "Invest in Marketing"]
    five_options = ["A", "B", "C", "D", "E"]

    assert app_module.build_pairs([]) == []
    assert app_module.build_pairs(["Only Option"]) == []
    assert len(app_module.build_pairs(two_options)) == 1
    assert len(app_module.build_pairs(five_options)) == 10


def test_comparison_options_are_the_implemented_saaty_menu(app_module):
    options = app_module.get_comparison_options("Cost", "Speed")

    assert options == [
        "Cost Extreme",
        "Cost Very Strong",
        "Cost Strong",
        "Cost Moderate",
        "Equal Importance",
        "Speed Moderate",
        "Speed Strong",
        "Speed Very Strong",
        "Speed Extreme"
    ]

    values = [
        app_module.convert_answer_to_saaty_value(
            option,
            "Cost",
            "Speed"
        )
        for option in options
    ]

    assert values == [
        9,
        7,
        5,
        3,
        1,
        1 / 3,
        1 / 5,
        1 / 7,
        1 / 9
    ]


def test_invalid_pairwise_answer_is_rejected_by_mapping(app_module):
    with pytest.raises(KeyError):
        app_module.convert_answer_to_saaty_value(
            "Cost Slightly",
            "Cost",
            "Speed"
        )


def test_incomplete_factor_comparisons_cannot_build_matrix(app_module):
    factors = ["Cost", "Speed", "Quality"]
    pairs = app_module.build_pairs(factors)
    incomplete_answers = {
        1: "Cost Strong",
        2: "Cost Moderate"
    }

    with pytest.raises(KeyError):
        app_module.build_comparison_matrix(
            factors,
            pairs,
            incomplete_answers
        )


def test_confidence_thresholds_around_consistency_ratio(app_module):
    assert app_module.get_decision_confidence(0.05)[0] == "Very High"
    assert app_module.get_decision_confidence(0.10)[0] == "High"
    assert app_module.get_decision_confidence(0.20)[0] == "High"
    assert app_module.get_decision_confidence(0.30)[0] == "Moderate"
    assert app_module.get_decision_confidence(0.31)[0] == "Low"


def test_consistency_ratio_above_and_below_point_one(app_module):
    consistent = np.array([
        [1, 2, 4],
        [1 / 2, 1, 2],
        [1 / 4, 1 / 2, 1]
    ])
    inconsistent = np.array([
        [1, 9, 1 / 9],
        [1 / 9, 1, 9],
        [9, 1 / 9, 1]
    ])

    consistent_cr = (
        app_module.calculate_ahp_results(consistent)
        ["consistency_ratio"]
    )
    inconsistent_cr = (
        app_module.calculate_ahp_results(inconsistent)
        ["consistency_ratio"]
    )

    assert consistent_cr <= 0.10
    assert inconsistent_cr > 0.10
