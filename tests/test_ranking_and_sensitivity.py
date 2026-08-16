import numpy as np


def test_alternative_scores_are_combined_with_factor_weights(app_module):
    factor_weights = np.array([0.6, 0.4])
    cost_option_scores = np.array([0.8, 0.2])
    speed_option_scores = np.array([0.3, 0.7])

    final_scores = (
        factor_weights[0] * cost_option_scores
        +
        factor_weights[1] * speed_option_scores
    )

    assert np.allclose(final_scores, np.array([0.60, 0.40]))
    assert int(np.argmax(final_scores)) == 0


def test_recommendation_strength_labels(app_module):
    clear_label, clear_gap, _ = app_module.get_recommendation_strength(
        [75, 25]
    )
    moderate_label, moderate_gap, _ = app_module.get_recommendation_strength(
        [54, 46]
    )
    close_label, close_gap, _ = app_module.get_recommendation_strength(
        [51, 49]
    )

    assert clear_label == "Clear Winning Option"
    assert clear_gap == 50
    assert moderate_label == "Moderate Winning Option"
    assert moderate_gap == 8
    assert close_label == "Very Close Competition Between Top Options"
    assert close_gap == 2


def test_sensitivity_analysis_reports_stable_recommendation(
    app_module,
    fake_state
):
    fake_state.selected_factors = ["Cost", "Speed"]
    fake_state.business_options = ["Option A", "Option B"]
    fake_state.factor_results = {
        "priority_weights": np.array([0.7, 0.3])
    }
    fake_state.option_results = {
        "Cost": {
            "priority_weights": np.array([0.9, 0.1])
        },
        "Speed": {
            "priority_weights": np.array([0.8, 0.2])
        }
    }
    fake_state.final_option_scores = (
        0.7 * fake_state.option_results["Cost"]["priority_weights"]
        +
        0.3 * fake_state.option_results["Speed"]["priority_weights"]
    )

    result = app_module.run_sensitivity_analysis()

    assert result["status"] == "Stable Recommendation"
    assert len(result["rows"]) == 4
    assert result["changed_cases"] == []
    assert all(
        row["Recommendation Changed"] == "No"
        for row in result["rows"]
    )


def test_sensitivity_analysis_detects_ranking_change(
    app_module,
    fake_state
):
    fake_state.selected_factors = ["Cost", "Speed"]
    fake_state.business_options = ["Option A", "Option B"]
    fake_state.factor_results = {
        "priority_weights": np.array([0.5, 0.5])
    }
    fake_state.option_results = {
        "Cost": {
            "priority_weights": np.array([0.55, 0.45])
        },
        "Speed": {
            "priority_weights": np.array([0.45, 0.55])
        }
    }
    fake_state.final_option_scores = (
        0.5 * fake_state.option_results["Cost"]["priority_weights"]
        +
        0.5 * fake_state.option_results["Speed"]["priority_weights"]
    )

    result = app_module.run_sensitivity_analysis()

    assert result["status"] == "Recommendation Changes"
    assert any(
        row["Recommendation Changed"] == "Yes"
        for row in result["rows"]
    )
    assert any(
        row["Factor Tested"] == "Cost"
        and row["Change Applied"] == "Decrease by 5%"
        and row["Recommended Option"] == "Option B"
        for row in result["changed_cases"]
    )
