from io import StringIO

import numpy as np
import pandas as pd


def _csv_value(frame, section, item, metric):
    matches = frame[
        (frame["Section"] == section)
        &
        (frame["Item"] == item)
        &
        (frame["Metric"] == metric)
    ]
    assert len(matches) == 1
    return str(matches.iloc[0]["Value"])


def test_end_to_end_decision_workflow_and_csv_export(
    app_module,
    fake_state
):
    fake_state.selected_factors = ["Cost", "Speed"]
    fake_state.comparison_pairs = app_module.build_pairs(
        fake_state.selected_factors
    )
    fake_state.comparison_answers = {
        1: "Cost Moderate"
    }
    fake_state.business_options = [
        "Open New Branch",
        "Invest in Marketing"
    ]
    fake_state.option_answers = {
        0: {
            1: "Invest in Marketing Strong"
        },
        1: {
            1: "Open New Branch Very Strong"
        }
    }

    app_module.recalculate_factor_results()
    app_module.calculate_all_option_results()

    final_scores = fake_state.final_option_scores
    best_index = int(np.argmax(final_scores))
    best_option = fake_state.business_options[best_index]
    sensitivity = app_module.run_sensitivity_analysis()
    confidence = app_module.get_decision_confidence(
        fake_state.factor_results["consistency_ratio"]
    )[0]
    evaluation = {
        "Was the recommendation easy to understand?": "Very Easy",
        "Did the recommendation reflect how you normally make business decisions?": "Partially",
        "Would you use this system again?": "Yes",
        "Additional comments": "Useful for comparing options."
    }

    csv_text = app_module.build_results_export_csv(
        "Demo SME",
        "Retail",
        confidence,
        best_option,
        sensitivity,
        evaluation
    )
    export_frame = pd.read_csv(
        StringIO(csv_text)
    )

    assert fake_state.factor_comparison_matrix.shape == (2, 2)
    assert np.allclose(
        fake_state.factor_results["priority_weights"],
        np.array([0.75, 0.25])
    )
    assert fake_state.option_matrices["Cost"].shape == (2, 2)
    assert fake_state.option_matrices["Speed"].shape == (2, 2)
    assert np.isclose(final_scores.sum(), 1)
    assert best_option == "Invest in Marketing"

    assert set(export_frame.columns) == {
        "Section",
        "Item",
        "Metric",
        "Value"
    }
    assert _csv_value(
        export_frame,
        "Metadata",
        "Business Name",
        "Optional"
    ) == "Demo SME"
    assert _csv_value(
        export_frame,
        "Metadata",
        "Industry",
        "Optional"
    ) == "Retail"
    assert _csv_value(
        export_frame,
        "Decision Setup",
        "Selected Factors",
        "List"
    ) == "Cost, Speed"
    assert _csv_value(
        export_frame,
        "Decision Setup",
        "Number of Factors",
        "Count"
    ) == "2"
    assert _csv_value(
        export_frame,
        "Consistency",
        "Decision Confidence",
        "Level"
    ) == confidence
    assert _csv_value(
        export_frame,
        "Recommendation",
        "Recommended Option",
        "Winner"
    ) == best_option
    assert _csv_value(
        export_frame,
        "Factor Comparison Answers",
        "Cost vs Speed",
        "Comparison Answer"
    ) == "Cost Moderate"
    assert _csv_value(
        export_frame,
        "Option Comparison Answers - Cost",
        "Open New Branch vs Invest in Marketing",
        "Comparison Answer"
    ) == "Invest in Marketing Strong"
    assert _csv_value(
        export_frame,
        "User Evaluation Responses",
        "Would you use this system again?",
        "Response"
    ) == "Yes"


def test_chart_data_is_sorted_and_rounded(app_module):
    chart_data = app_module.build_chart_data(
        ["A", "B", "C"],
        np.array([10.125, 55.555, 34.444]),
        "Score (%)"
    )

    assert list(chart_data.index) == ["B", "C", "A"]
    assert list(chart_data["Score (%)"]) == [55.55, 34.44, 10.12]


def test_flatten_comparison_answers_preserves_human_readable_pairs(
    app_module
):
    rows = app_module.flatten_comparison_answers(
        "Factor Comparison Answers",
        [("Cost", "Speed"), ("Cost", "Quality")],
        {
            1: "Cost Strong",
            2: "Equal Importance"
        }
    )

    assert rows == [
        {
            "Section": "Factor Comparison Answers",
            "Item": "Cost vs Speed",
            "Metric": "Comparison Answer",
            "Value": "Cost Strong"
        },
        {
            "Section": "Factor Comparison Answers",
            "Item": "Cost vs Quality",
            "Metric": "Comparison Answer",
            "Value": "Equal Importance"
        }
    ]
