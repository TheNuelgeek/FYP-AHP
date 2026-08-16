import numpy as np
import pytest


def test_saaty_answer_mapping_is_reciprocal(app_module):
    assert app_module.convert_answer_to_saaty_value(
        "Cost Strong",
        "Cost",
        "Speed"
    ) == 5

    assert app_module.convert_answer_to_saaty_value(
        "Speed Strong",
        "Cost",
        "Speed"
    ) == pytest.approx(1 / 5)

    assert app_module.convert_answer_to_saaty_value(
        "Equal Importance",
        "Cost",
        "Speed"
    ) == 1


def test_build_pairs_generates_upper_triangle_only(app_module):
    assert app_module.build_pairs(
        ["Cost", "Speed", "Quality"]
    ) == [
        ("Cost", "Speed"),
        ("Cost", "Quality"),
        ("Speed", "Quality")
    ]


def test_comparison_matrix_contains_diagonal_and_reciprocal_values(app_module):
    factors = ["Cost", "Speed", "Quality"]
    pairs = app_module.build_pairs(factors)
    answers = {
        1: "Cost Strong",
        2: "Quality Moderate",
        3: "Speed Very Strong"
    }

    matrix = app_module.build_comparison_matrix(
        factors,
        pairs,
        answers
    )

    expected = np.array([
        [1, 5, 1 / 3],
        [1 / 5, 1, 7],
        [3, 1 / 7, 1]
    ])

    assert np.allclose(matrix, expected)
    assert np.allclose(np.diag(matrix), np.ones(3))
    assert matrix[0, 1] == pytest.approx(1 / matrix[1, 0])
    assert matrix[0, 2] == pytest.approx(1 / matrix[2, 0])
    assert matrix[1, 2] == pytest.approx(1 / matrix[2, 1])


def test_ahp_normalization_weights_and_consistency_are_correct(app_module):
    matrix = np.array([
        [1, 3, 5],
        [1 / 3, 1, 2],
        [1 / 5, 1 / 2, 1]
    ])

    results = app_module.calculate_ahp_results(matrix)

    expected_column_totals = np.array([
        1 + 1 / 3 + 1 / 5,
        3 + 1 + 1 / 2,
        5 + 2 + 1
    ])
    expected_normalized = matrix / expected_column_totals
    expected_weights = expected_normalized.mean(axis=1)
    expected_weighted_sum = matrix.dot(expected_weights)
    expected_consistency_vector = (
        expected_weighted_sum / expected_weights
    )
    expected_lambda_max = expected_consistency_vector.mean()
    expected_ci = (expected_lambda_max - 3) / 2
    expected_cr = expected_ci / 0.58

    assert np.allclose(
        results["column_totals"],
        expected_column_totals
    )
    assert np.allclose(
        results["normalized_matrix"],
        expected_normalized
    )
    assert np.allclose(
        results["priority_weights"],
        expected_weights
    )
    assert np.allclose(
        results["importance_scores"],
        expected_weights * 100
    )
    assert results["lambda_max"] == pytest.approx(
        expected_lambda_max
    )
    assert results["consistency_index"] == pytest.approx(
        expected_ci
    )
    assert results["consistency_ratio"] == pytest.approx(
        expected_cr
    )


def test_two_item_matrix_has_zero_consistency_ratio(app_module):
    matrix = np.array([
        [1, 7],
        [1 / 7, 1]
    ])

    results = app_module.calculate_ahp_results(matrix)

    assert results["lambda_max"] == pytest.approx(2)
    assert results["consistency_index"] == 0
    assert results["consistency_ratio"] == 0
