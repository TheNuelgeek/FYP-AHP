from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from constants import (
    RANDOM_INDEX_TABLE,
    SUGGESTED_FACTORS
)


# =====================================================
# AHP HELPER FUNCTIONS
# =====================================================

def convert_answer_to_saaty_value(
    answer,
    first_item,
    second_item
):

    mapping = {

        f"{first_item} Extreme": 9,
        f"{first_item} Very Strong": 7,
        f"{first_item} Strong": 5,
        f"{first_item} Moderate": 3,

        "Equal Importance": 1,

        f"{second_item} Moderate": 1 / 3,
        f"{second_item} Strong": 1 / 5,
        f"{second_item} Very Strong": 1 / 7,
        f"{second_item} Extreme": 1 / 9
    }

    return mapping[answer]


def get_comparison_options(first_item, second_item):

    return [
        f"{first_item} Extreme",
        f"{first_item} Very Strong",
        f"{first_item} Strong",
        f"{first_item} Moderate",
        "Equal Importance",
        f"{second_item} Moderate",
        f"{second_item} Strong",
        f"{second_item} Very Strong",
        f"{second_item} Extreme"
    ]


def build_pairs(items):

    pairs = []

    for row in range(len(items)):

        for column in range(row + 1, len(items)):

            pairs.append(
                (
                    items[row],
                    items[column]
                )
            )

    return pairs


def calculate_ahp_results(comparison_matrix):

    # Column totals are used to normalize each comparison column.
    column_totals = comparison_matrix.sum(axis=0)

    normalized_matrix = (
        comparison_matrix / column_totals
    )

    # Row averages give the final AHP priority weights.
    priority_weights = (
        normalized_matrix.mean(axis=1)
    )

    weighted_sum_vector = np.dot(
        comparison_matrix,
        priority_weights
    )

    consistency_vector = (
        weighted_sum_vector / priority_weights
    )

    lambda_max = (
        consistency_vector.mean()
    )

    matrix_size = comparison_matrix.shape[0]

    if matrix_size <= 2:

        consistency_index = 0

    else:

        consistency_index = (
            (lambda_max - matrix_size)
            /
            (matrix_size - 1)
        )

    random_index = RANDOM_INDEX_TABLE.get(
        matrix_size,
        1.49
    )

    if random_index == 0:

        consistency_ratio = 0

    else:

        consistency_ratio = (
            consistency_index / random_index
        )

    return {
        "column_totals": column_totals,
        "normalized_matrix": normalized_matrix,
        "priority_weights": priority_weights,
        "importance_scores": priority_weights * 100,
        "lambda_max": lambda_max,
        "consistency_index": consistency_index,
        "consistency_ratio": consistency_ratio
    }


def build_comparison_matrix(items, pairs, answers):

    number_of_items = len(items)

    comparison_matrix = np.ones(
        (
            number_of_items,
            number_of_items
        )
    )

    for pair_counter, pair in enumerate(pairs, start=1):

        first_item = pair[0]
        second_item = pair[1]

        row = items.index(first_item)
        column = items.index(second_item)

        answer = answers[pair_counter]

        saaty_value = convert_answer_to_saaty_value(
            answer,
            first_item,
            second_item
        )

        comparison_matrix[row][column] = (
            saaty_value
        )

        comparison_matrix[column][row] = (
            1 / saaty_value
        )

    return comparison_matrix


def matrix_dataframe(matrix, labels):

    return pd.DataFrame(
        np.round(matrix, 3),
        index=labels,
        columns=labels
    )


def scores_dataframe(items, scores):

    return pd.DataFrame({
        "Item": items,
        "Score": [
            f"{score:.2f}%"
            for score in scores
        ]
    })


def get_decision_confidence(consistency_ratio):

    if consistency_ratio <= 0.05:

        return (
            "Very High",
            "Your priorities were expressed very clearly.",
            "The recommendation closely reflects the preferences you provided.",
            "success"
        )

    if consistency_ratio <= 0.20:

        return (
            "High",
            "Your priorities were expressed consistently.",
            "The recommendation is a strong reflection of the preferences you provided.",
            "success"
        )

    if consistency_ratio <= 0.30:

        return (
            "Moderate",
            "Some of your priorities compete with one another.",
            "The recommendation is still useful, but small changes to your responses could affect the final ranking.",
            "warning"
        )

    return (
        "Low",
        "Several priorities are pulling in different directions.",
        "The recommendation is available, but it should be interpreted with additional caution.",
        "error"
    )


def render_factor_technical_analysis(results, comparison_matrix, factors):

    st.subheader(
        "Comparison Matrix"
    )

    st.dataframe(
        matrix_dataframe(
            comparison_matrix,
            factors
        ),
        use_container_width=True
    )

    st.write(
        "The comparison matrix stores the pairwise judgments entered during the decision process."
    )

    st.subheader(
        "Column Totals"
    )

    st.dataframe(
        pd.DataFrame({
            "Factor": factors,
            "Column Total": np.round(
                results["column_totals"],
                4
            )
        }),
        use_container_width=True
    )

    st.write(
        "Column totals are used to normalize the comparison matrix so that comparisons can be evaluated on a common scale."
    )

    st.subheader(
        "Normalized Matrix"
    )

    st.dataframe(
        matrix_dataframe(
            results["normalized_matrix"],
            factors
        ),
        use_container_width=True
    )

    st.write(
        "The normalized matrix converts comparison values into proportional scores used to calculate factor importance weights."
    )

    st.subheader(
        "Priority Weights (Eigenvector)"
    )

    st.dataframe(
        pd.DataFrame({
            "Factor": factors,
            "Priority Weight": np.round(
                results["priority_weights"],
                4
            )
        }),
        use_container_width=True
    )

    st.write(
        "Priority weights are calculated by averaging each row of the normalized matrix. "
        "These values are the technical basis for the factor importance percentages shown above."
    )

    st.divider()

    st.write(
        f"**Lambda Max (λmax): "
        f"{results['lambda_max']:.4f}**"
    )

    st.write(
        "Measures how closely the comparison matrix follows "
        "perfect logical consistency."
    )

    st.write(
        f"**Consistency Index (CI): "
        f"{results['consistency_index']:.4f}**"
    )

    st.write(
        "Measures the amount of inconsistency present in the "
        "comparison judgments."
    )

    st.write(
        f"**Consistency Ratio (CR): "
        f"{results['consistency_ratio']:.4f}**"
    )

    st.write(
        "Decision Confidence is derived from this value. "
        "Lower values generally indicate that the recommendation more closely reflects the priorities entered during evaluation."
    )


def display_consistency_feedback(results, comparison_matrix, factors):

    consistency_ratio = results["consistency_ratio"]

    (
        confidence_label,
        confidence_summary,
        confidence_detail,
        confidence_status
    ) = get_decision_confidence(
        consistency_ratio
    )

    if consistency_ratio <= 0.10:

        st.success(
            f"Decision Confidence: {confidence_label}"
        )

        st.write(
            "This means your judgments followed a logical "
            "pattern and the recommendation can be considered reliable."
        )

        st.write(
            confidence_summary
        )

        st.write(
            confidence_detail
        )

    elif confidence_status == "warning":

        st.warning(
            f"Decision Confidence: {confidence_label}"
        )

        st.write(
            confidence_summary
        )

        st.write(
            confidence_detail
        )

    else:

        st.error(
            f"Decision Confidence: {confidence_label}"
        )

        st.write(
            confidence_summary
        )

        st.write(
            confidence_detail
        )

        st.write(
            "You may review your comparisons if you would like a more stable result."
        )

    st.caption(
        f"Decision Confidence Level: {confidence_label}"
    )

    with st.expander(
        "Show Technical Analysis"
    ):
        render_factor_technical_analysis(
            results,
            comparison_matrix,
            factors
        )


def option_comparisons_are_complete():

    option_pairs = build_pairs(
        st.session_state.business_options
    )

    if not option_pairs:

        return False

    for factor_index in range(
        len(st.session_state.selected_factors)
    ):

        factor_answers = (
            st.session_state
            .option_answers
            .get(factor_index, {})
        )

        if len(factor_answers) < len(option_pairs):

            return False

    return True


def recalculate_factor_results():

    comparison_matrix = build_comparison_matrix(
        st.session_state.selected_factors,
        st.session_state.comparison_pairs,
        st.session_state.comparison_answers
    )

    st.session_state.factor_comparison_matrix = (
        comparison_matrix
    )

    st.session_state.factor_results = (
        calculate_ahp_results(
            comparison_matrix
        )
    )

    if option_comparisons_are_complete():

        calculate_all_option_results()


def get_factor_influence_feedback(factors, importance_scores):

    top_index = int(
        np.argmax(importance_scores)
    )

    top_factor = factors[top_index]
    top_score = importance_scores[top_index]

    if top_score >= 50:

        return (
            "Dominant Factor Present",
            f"{top_factor} carries {top_score:.2f}% of the total "
            "importance. It is likely to have a particularly strong "
            "effect on the final recommendation."
        )

    return (
        "Balanced Factor Distribution",
        f"No single factor exceeds 50% importance. Your recommendation "
        f"will therefore reflect a broader balance across the selected "
        f"factors, led by {top_factor} at {top_score:.2f}%."
    )


def get_recommendation_strength(sorted_scores):

    score_gap = (
        sorted_scores[0] - sorted_scores[1]
    )

    if score_gap >= 15:

        return (
            "Clear Winning Option",
            score_gap,
            "The leading option has a substantial advantage over the "
            "second-ranked option."
        )

    if score_gap >= 5:

        return (
            "Moderate Winning Option",
            score_gap,
            "The leading option has a meaningful advantage, although "
            "the second-ranked option remains competitive."
        )

    return (
        "Very Close Competition Between Top Options",
        score_gap,
        "The top two options are closely matched. Practical constraints "
        "and business judgment should play an important role in the "
        "final choice."
    )


def build_chart_data(items, scores, column_name):

    sorted_indexes = np.argsort(scores)[::-1]

    return pd.DataFrame(
        {
            column_name: [
                round(float(scores[index]), 2)
                for index in sorted_indexes
            ]
        },
        index=[
            items[index]
            for index in sorted_indexes
        ]
    )


def run_sensitivity_analysis():

    selected_factors = st.session_state.selected_factors
    business_options = st.session_state.business_options
    factor_weights = (
        st.session_state
        .factor_results["priority_weights"]
    )
    original_scores = st.session_state.final_option_scores
    original_best_index = int(
        np.argmax(original_scores)
    )
    original_best_option = business_options[original_best_index]
    rows = []
    changed_cases = []

    for factor_index, factor in enumerate(selected_factors):

        for direction, multiplier in [
            ("Increase by 5%", 1.05),
            ("Decrease by 5%", 0.95)
        ]:

            adjusted_weights = factor_weights.copy()
            adjusted_weights[factor_index] = (
                adjusted_weights[factor_index]
                *
                multiplier
            )
            adjusted_weights = (
                adjusted_weights / adjusted_weights.sum()
            )

            adjusted_scores = np.zeros(
                len(business_options)
            )

            for option_factor_index, option_factor in enumerate(
                selected_factors
            ):

                adjusted_scores += (
                    adjusted_weights[option_factor_index]
                    *
                    st.session_state
                    .option_results[option_factor]["priority_weights"]
                )

            adjusted_best_index = int(
                np.argmax(adjusted_scores)
            )
            adjusted_best_option = (
                business_options[adjusted_best_index]
            )
            changed = (
                adjusted_best_option != original_best_option
            )

            row = {
                "Factor Tested": factor,
                "Change Applied": direction,
                "Recommended Option": adjusted_best_option,
                "Recommendation Changed": "Yes" if changed else "No"
            }

            rows.append(row)

            if changed:

                changed_cases.append(row)

    status = (
        "Recommendation Changes"
        if changed_cases
        else "Stable Recommendation"
    )

    return {
        "status": status,
        "rows": rows,
        "changed_cases": changed_cases
    }


def flatten_comparison_answers(title, pairs, answers):

    rows = []

    for pair_number, pair in enumerate(
        pairs,
        start=1
    ):

        rows.append({
            "Section": title,
            "Item": f"{pair[0]} vs {pair[1]}",
            "Metric": "Comparison Answer",
            "Value": answers[pair_number]
        })

    return rows


def build_results_export_csv(
    business_name,
    industry,
    decision_confidence,
    best_option,
    sensitivity_result,
    evaluation_responses
):

    rows = []

    def add_row(section, item, metric, value):

        rows.append({
            "Section": section,
            "Item": item,
            "Metric": metric,
            "Value": value
        })

    add_row(
        "Metadata",
        "Generated At",
        "Timestamp",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    add_row("Metadata", "Business Name", "Optional", business_name)
    add_row("Metadata", "Industry", "Optional", industry)
    add_row(
        "Decision Setup",
        "Selected Factors",
        "List",
        ", ".join(st.session_state.selected_factors)
    )
    add_row(
        "Decision Setup",
        "Number of Factors",
        "Count",
        len(st.session_state.selected_factors)
    )

    for factor, score in zip(
        st.session_state.selected_factors,
        st.session_state.factor_results["importance_scores"]
    ):

        add_row(
            "Factor Importance Scores",
            factor,
            "Importance (%)",
            f"{score:.2f}"
        )

    add_row(
        "Consistency",
        "Consistency Ratio",
        "CR",
        f"{st.session_state.factor_results['consistency_ratio']:.4f}"
    )
    add_row(
        "Consistency",
        "Decision Confidence",
        "Level",
        decision_confidence
    )
    add_row(
        "Business Options",
        "Options Compared",
        "List",
        ", ".join(st.session_state.business_options)
    )

    for option, score in zip(
        st.session_state.business_options,
        st.session_state.final_option_scores * 100
    ):

        add_row(
            "Final Option Scores",
            option,
            "Overall Score (%)",
            f"{score:.2f}"
        )

    add_row(
        "Recommendation",
        "Recommended Option",
        "Winner",
        best_option
    )

    rows.extend(
        flatten_comparison_answers(
            "Factor Comparison Answers",
            st.session_state.comparison_pairs,
            st.session_state.comparison_answers
        )
    )

    option_pairs = build_pairs(
        st.session_state.business_options
    )

    for factor_index, factor in enumerate(
        st.session_state.selected_factors
    ):

        factor_option_answers = (
            st.session_state
            .option_answers
            .get(factor_index, {})
        )

        for row in flatten_comparison_answers(
            f"Option Comparison Answers - {factor}",
            option_pairs,
            factor_option_answers
        ):

            rows.append(row)

    add_row(
        "Sensitivity Analysis",
        "Overall Result",
        "Status",
        sensitivity_result["status"]
    )

    for row in sensitivity_result["rows"]:

        add_row(
            "Sensitivity Analysis",
            f"{row['Factor Tested']} - {row['Change Applied']}",
            "Recommended Option",
            row["Recommended Option"]
        )

        add_row(
            "Sensitivity Analysis",
            f"{row['Factor Tested']} - {row['Change Applied']}",
            "Recommendation Changed",
            row["Recommendation Changed"]
        )

    for question, answer in evaluation_responses.items():

        add_row(
            "User Evaluation Responses",
            question,
            "Response",
            answer
        )

    return pd.DataFrame(rows).to_csv(index=False)


def reset_factor_comparison_state():

    st.session_state.comparison_pairs = []
    st.session_state.comparison_index = 0
    st.session_state.comparison_answers = {}
    st.session_state.factor_comparison_matrix = None
    st.session_state.factor_results = None


def reset_option_state():

    st.session_state.business_options = []
    st.session_state.option_factor_index = 0
    st.session_state.option_pair_index = 0
    st.session_state.option_answers = {}
    st.session_state.option_matrices = {}
    st.session_state.option_results = {}
    st.session_state.final_option_scores = None

    for state_key in [
        "export_business_name",
        "export_industry",
        "evaluation_understanding",
        "evaluation_reflected_decision",
        "evaluation_use_again",
        "evaluation_comments"
    ]:

        st.session_state.pop(
            state_key,
            None
        )


def calculate_all_option_results():

    business_options = st.session_state.business_options
    selected_factors = st.session_state.selected_factors
    all_option_results = {}
    all_option_matrices = {}

    for factor_index, factor in enumerate(selected_factors):

        pairs = build_pairs(business_options)
        answers = (
            st.session_state
            .option_answers
            .get(factor_index, {})
        )

        option_matrix = build_comparison_matrix(
            business_options,
            pairs,
            answers
        )

        option_results = calculate_ahp_results(
            option_matrix
        )

        all_option_matrices[factor] = option_matrix
        all_option_results[factor] = option_results

    factor_weights = (
        st.session_state
        .factor_results["priority_weights"]
    )

    final_scores = np.zeros(
        len(business_options)
    )

    for factor_index, factor in enumerate(selected_factors):

        final_scores += (
            factor_weights[factor_index]
            *
            all_option_results[factor]["priority_weights"]
        )

    st.session_state.option_matrices = all_option_matrices
    st.session_state.option_results = all_option_results
    st.session_state.final_option_scores = final_scores


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="SME Decision Support System",
    layout="wide"
)

st.markdown(
    """
    <style>
        :root {
            --primary-bg: #003A86;
            --primary-text: #FFFFFF;
            --accent: #FFC222;
            --secondary-accent: #D0F7FF;
            --surface: #FFFFFF;
            --surface-soft: #F5F9FF;
            --border: #D8E4F2;
            --body-text: #14324A;
        }

        .stApp,
        [data-testid="stAppViewContainer"] {
            background: var(--primary-bg) !important;
            color: var(--body-text);
        }

        [data-testid="stMain"] {
            background: transparent !important;
        }

        .block-container {
            background: var(--surface);
            border: 1px solid rgba(208, 247, 255, 0.45);
            border-radius: 8px;
            box-shadow: 0 18px 50px rgba(0, 20, 60, 0.22);
            width: min(1440px, calc(100% - 3rem));
            margin: 2.25rem auto 2rem auto;
            padding: 3rem 3.5rem 3.5rem 3.5rem;
        }

        h1 {
            color: var(--primary-bg);
            font-size: 2.55rem;
            font-weight: 800;
            letter-spacing: 0;
            margin-bottom: 0.75rem;
        }

        h2, h3 {
            color: var(--primary-bg);
            font-weight: 760;
            letter-spacing: 0;
        }

        [data-testid="stHeader"] {
            background: var(--primary-bg) !important;
            border-bottom: 4px solid var(--accent);
        }

        [data-testid="stToolbar"] {
            color: var(--primary-text) !important;
        }

        .block-container p,
        .block-container li,
        .block-container label,
        .block-container span,
        .block-container div {
            color: var(--body-text);
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--border);
            color: var(--body-text);
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span {
            color: var(--body-text) !important;
            font-weight: 600;
        }

        div[data-testid="stInfo"] {
            background: var(--secondary-accent) !important;
        }

        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] label span,
        [data-testid="stRadio"] label,
        [data-testid="stRadio"] label span {
            color: var(--body-text) !important;
            font-weight: 600;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: var(--primary-bg);
            color: var(--primary-text);
            border: 1px solid var(--primary-bg);
            border-radius: 6px;
            font-weight: 700;
            padding: 0.55rem 1rem;
            box-shadow: 0 8px 18px rgba(0, 58, 134, 0.18);
        }

        .stButton > button *,
        .stDownloadButton > button * {
            color: var(--primary-text) !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: var(--accent);
            color: var(--primary-bg);
            border-color: var(--accent);
        }

        .stButton > button:hover *,
        .stDownloadButton > button:hover * {
            color: var(--primary-bg) !important;
        }

        .stButton > button:disabled {
            background: #9AAFC9;
            color: #FFFFFF;
            border-color: #9AAFC9;
            box-shadow: none;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input {
            background: #FFFFFF !important;
            color: var(--body-text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 6px !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: var(--primary-bg) !important;
            box-shadow: 0 0 0 2px rgba(208, 247, 255, 0.9) !important;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            border-top: 4px solid var(--accent);
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--primary-bg) !important;
        }

        div[data-testid="stExpander"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            background: #FFFFFF;
        }

        [data-testid="stVegaLiteChart"] {
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem;
        }

        .app-panel {
            background: var(--secondary-accent);
            border: 1px solid var(--border);
            border-left: 6px solid var(--accent);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 0.8rem 0 1rem 0;
        }

        .app-panel strong {
            color: var(--primary-bg);
        }

        hr {
            border-color: var(--border);
        }

        @media (max-width: 768px) {
            .block-container {
                border-radius: 0;
                width: 100%;
                margin-top: 0;
                margin-bottom: 0;
                padding: 2rem 1.25rem;
            }

            h1 {
                font-size: 2rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# SESSION STATE
# =====================================================

if "page" not in st.session_state:

    st.session_state.page = (
        "factor_selection"
    )

if "custom_factors" not in st.session_state:

    st.session_state.custom_factors = []

if "selected_factors" not in st.session_state:

    st.session_state.selected_factors = []

if "comparison_pairs" not in st.session_state:

    st.session_state.comparison_pairs = []

if "comparison_index" not in st.session_state:

    st.session_state.comparison_index = 0

if "comparison_answers" not in st.session_state:

    st.session_state.comparison_answers = {}

if "factor_comparison_matrix" not in st.session_state:

    st.session_state.factor_comparison_matrix = None

if "factor_results" not in st.session_state:

    st.session_state.factor_results = None

if "business_options" not in st.session_state:

    st.session_state.business_options = []

if "option_factor_index" not in st.session_state:

    st.session_state.option_factor_index = 0

if "option_pair_index" not in st.session_state:

    st.session_state.option_pair_index = 0

if "option_answers" not in st.session_state:

    st.session_state.option_answers = {}

if "option_matrices" not in st.session_state:

    st.session_state.option_matrices = {}

if "option_results" not in st.session_state:

    st.session_state.option_results = {}

if "final_option_scores" not in st.session_state:

    st.session_state.final_option_scores = None

if "comparison_update_message" not in st.session_state:

    st.session_state.comparison_update_message = ""


# =====================================================
# PAGE 1:
# FACTOR SELECTION
# =====================================================

if (
    st.session_state.page
    ==
    "factor_selection"
):

    st.title(
        "SME Decision Support System"
    )

    st.write(
        """
        This system helps SME owners evaluate
        business decisions using the
        Analytic Hierarchy Process (AHP).
        """
    )

    st.subheader(
        "Decision Factor Selection"
    )

    st.write(
        """
        Suggested decision factors are based on
        common SME operational priorities.

        You may:
        - Select suggested factors
        - Add your own custom factors
        - Combine both approaches
        """
    )

    selected_factors = []

    all_factors = (
        SUGGESTED_FACTORS
        +
        st.session_state.custom_factors
    )

    for factor in all_factors:

        is_selected = st.checkbox(
            factor,
            value=factor in st.session_state.selected_factors,
            key=f"factor_checkbox_{factor}"
        )

        if is_selected:

            selected_factors.append(
                factor
            )

    st.divider()

    custom_factor = st.text_input(
        "Add Custom Factor"
    )

    if st.button("Add Factor"):

        cleaned_factor = (
            custom_factor.strip().title()
        )

        if cleaned_factor == "":

            st.warning(
                "Factor name cannot be empty."
            )

        else:

            existing_factors = [

                factor.lower()

                for factor in (
                    SUGGESTED_FACTORS
                    +
                    st.session_state.custom_factors
                )
            ]

            if (
                cleaned_factor.lower()
                in
                existing_factors
            ):

                st.warning(
                    "That factor already exists."
                )

            else:

                st.session_state.custom_factors.append(
                    cleaned_factor
                )

                st.rerun()

    st.divider()

    if selected_factors:

        st.success(
            f"{len(selected_factors)} factor(s) selected"
        )

        for factor in selected_factors:

            st.write(
                f"- {factor}"
            )

    else:

        st.warning(
            "No decision factors selected."
        )

    st.divider()

    if st.button(
        "Continue to Comparisons"
    ):

        if len(selected_factors) < 2:

            st.error(
                "Please select at least two factors."
            )

        else:

            st.session_state.selected_factors = (
                selected_factors
            )

            reset_factor_comparison_state()
            reset_option_state()

            st.session_state.page = (
                "factor_comparison"
            )

            st.rerun()


# =====================================================
# PAGE 2:
# FACTOR COMPARISON
# =====================================================

elif (
    st.session_state.page
    ==
    "factor_comparison"
):

    if len(
        st.session_state.comparison_pairs
    ) == 0:

        st.session_state.comparison_pairs = (
            build_pairs(
                st.session_state.selected_factors
            )
        )

    current_pair = (
        st.session_state.comparison_pairs[
            st.session_state.comparison_index
        ]
    )

    first_factor = current_pair[0]
    second_factor = current_pair[1]

    total_comparisons = len(
        st.session_state.comparison_pairs
    )

    current_number = (
        st.session_state.comparison_index
        +
        1
    )

    st.title(
        "Factor Comparison"
    )

    st.progress(
        current_number
        /
        total_comparisons
    )

    st.write(
        f"Comparison {current_number} of {total_comparisons}"
    )

    st.subheader(
        f"{first_factor} vs {second_factor}"
    )

    st.info(
    f"""
    You are deciding which factors should have the greatest influence
    on the final recommendation.

    If **{first_factor}** and **{second_factor}** lead to different business
    choices, which one should have greater influence on the final decision?
    """
    )

    comparison_options = get_comparison_options(
        first_factor,
        second_factor
    )

    saved_answer = (
        st.session_state
        .comparison_answers
        .get(
            current_number,
            comparison_options[0]
        )
    )

    comparison_choice = st.radio(

        "Select the option that best reflects your judgement:",

        comparison_options,

        index=comparison_options.index(saved_answer),
        key=f"comparison_{current_number}"
    )

    left_column, middle_column, right_column = st.columns(3)

    with left_column:

        if st.button(
            "Back to Factor Selection"
        ):

            st.session_state.page = (
                "factor_selection"
            )

            st.rerun()

    with middle_column:

        if st.button(
            "Previous Comparison",
            disabled=st.session_state.comparison_index == 0
        ):

            # Save any edit made on this screen before moving backward.
            st.session_state.comparison_answers[
                current_number
            ] = comparison_choice

            st.session_state.comparison_index -= 1

            st.rerun()

    with right_column:

        if st.button(
            "Next Comparison"
        ):

            st.session_state.comparison_answers[
                current_number
            ] = comparison_choice

            if (
                st.session_state.comparison_index
                <
                total_comparisons - 1
            ):

                st.session_state.comparison_index += 1

                st.rerun()

            else:

                recalculate_factor_results()

                st.session_state.page = (
                    "factor_results"
                )

                st.rerun()


# =====================================================
# PAGE 3:
# FACTOR RESULTS AND CONSISTENCY ANALYSIS
# =====================================================

elif (
    st.session_state.page
    ==
    "factor_results"
):

    factors = st.session_state.selected_factors
    comparison_matrix = (
        st.session_state.factor_comparison_matrix
    )
    results = st.session_state.factor_results

    if comparison_matrix is None or results is None:

        st.error(
            "Factor results are not available yet. "
            "Please complete the factor comparisons first."
        )

        if st.button("Return to Comparisons"):

            st.session_state.page = (
                "factor_comparison"
            )

            st.rerun()

    else:

        st.title(
            "Factor Results"
        )

        st.write(
            "These results show which decision factors matter "
            "most in your business decision."
        )

        st.subheader(
            "Factor Importance Scores"
        )

        sorted_indexes = np.argsort(
            results["importance_scores"]
        )[::-1]

        sorted_factors = [
            factors[index]
            for index in sorted_indexes
        ]

        sorted_scores = [
            results["importance_scores"][index]
            for index in sorted_indexes
        ]

        st.dataframe(
            scores_dataframe(
                sorted_factors,
                sorted_scores
            ),
            use_container_width=True
        )

        factor_chart_data = pd.DataFrame(
            {
                "Importance (%)": sorted_scores
            },
            index=sorted_factors
        )

        st.bar_chart(
            factor_chart_data,
            color="#003A86"
        )

        top_factor_index = int(
            np.argmax(
                results["importance_scores"]
            )
        )

        top_factor = factors[top_factor_index]
        top_score = results["importance_scores"][top_factor_index]

        st.success(
            f"Highest-ranked factor: {top_factor} "
            f"({top_score:.2f}% importance)."
        )

        st.write(
            f"This means {top_factor} has the strongest influence "
            "on the final recommendation based on your judgments."
        )

        influence_label, influence_message = (
            get_factor_influence_feedback(
                factors,
                results["importance_scores"]
            )
        )

        st.info(
            f"{influence_label}: {influence_message}"
        )

        st.subheader(
            "Consistency Analysis"
        )

        display_consistency_feedback(
            results, comparison_matrix, factors
        )

        st.divider()

        left_column, right_column = st.columns(2)

        with left_column:

            if st.button(
                "Review Factor Comparisons"
            ):

                st.session_state.page = (
                    "factor_comparison_review"
                )

                st.rerun()

        with right_column:

            if st.button(
                "Continue to Business Options"
            ):

                reset_option_state()

                st.session_state.page = (
                    "option_setup"
                )

                st.rerun()


# =====================================================
# PAGE 4:
# FACTOR COMPARISON REVIEW
# =====================================================

elif (
    st.session_state.page
    ==
    "factor_comparison_review"
):

    factors = st.session_state.selected_factors
    comparison_pairs = st.session_state.comparison_pairs
    comparison_answers = st.session_state.comparison_answers

    st.title(
        "Review Factor Comparisons"
    )

    st.write(
        "Review all completed judgments below. Select one comparison "
        "to edit it without restarting the full comparison process."
    )

    if st.session_state.comparison_update_message:

        st.success(
            st.session_state.comparison_update_message
        )

        st.session_state.comparison_update_message = ""

    review_rows = []

    for pair_number, pair in enumerate(
        comparison_pairs,
        start=1
    ):

        review_rows.append({
            "Comparison": f"{pair[0]} vs {pair[1]}",
            "Judgment": comparison_answers[pair_number]
        })

    st.dataframe(
        pd.DataFrame(review_rows),
        use_container_width=True,
        hide_index=True
    )

    comparison_labels = [
        (
            f"{pair[0]} vs {pair[1]} -> "
            f"{comparison_answers[pair_number]}"
        )
        for pair_number, pair in enumerate(
            comparison_pairs,
            start=1
        )
    ]

    selected_review_index = st.selectbox(
        "Select a comparison to edit",
        range(len(comparison_labels)),
        format_func=lambda index: comparison_labels[index]
    )

    selected_pair = comparison_pairs[
        selected_review_index
    ]

    review_number = selected_review_index + 1
    review_options = get_comparison_options(
        selected_pair[0],
        selected_pair[1]
    )

    current_review_answer = comparison_answers[
        review_number
    ]

    updated_review_answer = st.radio(
        (
            f"Update {selected_pair[0]} vs "
            f"{selected_pair[1]}"
        ),
        review_options,
        index=review_options.index(
            current_review_answer
        ),
        key=f"review_factor_answer_{review_number}"
    )

    left_column, right_column = st.columns(2)

    with left_column:

        if st.button(
            "Save Comparison Update"
        ):

            st.session_state.comparison_answers[
                review_number
            ] = updated_review_answer

            # Recreate the step-by-step widget from the updated answer.
            st.session_state.pop(
                f"comparison_{review_number}",
                None
            )

            recalculate_factor_results()

            st.session_state.comparison_update_message = (
                "Comparison updated. Factor scores and consistency "
                "results have been recalculated."
            )

            st.rerun()

    with right_column:

        if st.button(
            "Return to Factor Results"
        ):

            st.session_state.page = (
                "factor_results"
            )

            st.rerun()


# =====================================================
# PAGE 5:
# BUSINESS OPTION SETUP
# =====================================================

elif (
    st.session_state.page
    ==
    "option_setup"
):

    st.title(
        "Business Option Setup"
    )

    st.write(
        """
        Business options are the alternatives you want the
        system to evaluate.

        Examples:
        - Open New Branch
        - Invest in Marketing
        - Hire Sales Staff
        """
    )

    number_of_options = st.number_input(
        "How many business options would you like to compare?",
        min_value=2,
        max_value=5,
        value=2,
        step=1
    )

    entered_options = []

    for option_number in range(
        1,
        int(number_of_options) + 1
    ):

        option_name = st.text_input(
            f"Business Option {option_number}",
            key=f"business_option_{option_number}"
        ).strip()

        entered_options.append(
            option_name
        )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:

        if st.button(
            "Back to Factor Results"
        ):

            st.session_state.page = (
                "factor_results"
            )

            st.rerun()

    with right_column:

        if st.button(
            "Continue to Option Comparisons"
        ):

            cleaned_options = [
                option
                for option in entered_options
                if option != ""
            ]

            unique_options = []

            for option in cleaned_options:

                if option.lower() not in [
                    existing_option.lower()
                    for existing_option in unique_options
                ]:

                    unique_options.append(
                        option
                    )

            if len(cleaned_options) != int(number_of_options):

                st.error(
                    "Please enter a name for every business option."
                )

            elif len(unique_options) != len(cleaned_options):

                st.error(
                    "Business option names must be different."
                )

            else:

                st.session_state.business_options = (
                    unique_options
                )

                st.session_state.option_factor_index = 0
                st.session_state.option_pair_index = 0
                st.session_state.option_answers = {}
                st.session_state.option_matrices = {}
                st.session_state.option_results = {}
                st.session_state.final_option_scores = None

                st.session_state.page = (
                    "option_comparison"
                )

                st.rerun()


# =====================================================
# PAGE 5:
# BUSINESS OPTION COMPARISON
# =====================================================

elif (
    st.session_state.page
    ==
    "option_comparison"
):

    business_options = st.session_state.business_options
    selected_factors = st.session_state.selected_factors
    option_pairs = build_pairs(
        business_options
    )

    if len(business_options) < 2:

        st.error(
            "Please enter at least two business options first."
        )

        if st.button("Return to Business Option Setup"):

            st.session_state.page = (
                "option_setup"
            )

            st.rerun()

    else:

        factor_index = st.session_state.option_factor_index
        pair_index = st.session_state.option_pair_index

        selected_factor = selected_factors[factor_index]
        current_pair = option_pairs[pair_index]

        first_option = current_pair[0]
        second_option = current_pair[1]

        total_option_comparisons = (
            len(option_pairs)
            *
            len(selected_factors)
        )

        completed_option_comparisons = (
            factor_index
            *
            len(option_pairs)
            +
            pair_index
            +
            1
        )

        st.title(
            "Business Option Comparison"
        )

        st.progress(
            completed_option_comparisons
            /
            total_option_comparisons
        )

        st.write(
            f"Comparison {completed_option_comparisons} "
            f"of {total_option_comparisons}"
        )

        st.subheader(
            f"Factor: {selected_factor}"
        )

        st.info(
            f"""
            Considering **{selected_factor}** only:

            If all other factors were ignored,
            which option performs better under **{selected_factor}**?

            Focus only on **{selected_factor}**
            when making your choice.
            """
        )

        option_comparison_options = get_comparison_options(
            first_option,
            second_option
        )

        saved_option_answer = (
            st.session_state
            .option_answers
            .get(factor_index, {})
            .get(
                pair_index + 1,
                option_comparison_options[0]
            )
        )

        # Recreate the radio with its saved value when navigating backward.
        comparison_choice = st.radio(

            f"{first_option} vs {second_option}",

            option_comparison_options,

            index=option_comparison_options.index(
                saved_option_answer
            ),
            key=(
                f"option_comparison_"
                f"{factor_index}_{pair_index}"
            )
        )

        st.write(
            "Use Moderate for a small practical advantage, "
            "Strong for a clear advantage, and Extreme only "
            "when the difference is very large."
        )

        left_column, middle_column, right_column = st.columns(3)

        with left_column:

            if st.button(
                "Back to Business Options"
            ):

                st.session_state.page = (
                    "option_setup"
                )

                st.rerun()

        with middle_column:

            if st.button(
                "Previous Comparison",
                disabled=completed_option_comparisons == 1
            ):

                if (
                    factor_index
                    not in st.session_state.option_answers
                ):

                    st.session_state.option_answers[
                        factor_index
                    ] = {}

                # Save any edit made on this screen before moving backward.
                st.session_state.option_answers[
                    factor_index
                ][pair_index + 1] = comparison_choice

                if pair_index > 0:

                    st.session_state.option_pair_index -= 1

                else:

                    st.session_state.option_factor_index -= 1
                    st.session_state.option_pair_index = (
                        len(option_pairs) - 1
                    )

                st.rerun()

        with right_column:

            if st.button(
                "Next Option Comparison"
            ):

                if (
                    factor_index
                    not in st.session_state.option_answers
                ):

                    st.session_state.option_answers[
                        factor_index
                    ] = {}

                st.session_state.option_answers[
                    factor_index
                ][pair_index + 1] = comparison_choice

                if pair_index < len(option_pairs) - 1:

                    st.session_state.option_pair_index += 1

                    st.rerun()

                elif factor_index < len(selected_factors) - 1:

                    st.session_state.option_factor_index += 1
                    st.session_state.option_pair_index = 0

                    st.rerun()

                else:

                    calculate_all_option_results()

                    st.session_state.page = (
                        "final_results"
                    )

                    st.rerun()


# =====================================================
# PAGE 6:
# FINAL BUSINESS RECOMMENDATION
# =====================================================

elif (
    st.session_state.page
    ==
    "final_results"
):

    business_options = st.session_state.business_options
    final_scores = st.session_state.final_option_scores

    if final_scores is None:

        st.error(
            "Final results are not available yet. "
            "Please complete the business option comparisons first."
        )

        if st.button("Return to Option Comparisons"):

            st.session_state.page = (
                "option_comparison"
            )

            st.rerun()

    else:

        st.title(
            "Final Business Recommendation"
        )

        final_percentages = (
            final_scores * 100
        )

        sorted_indexes = np.argsort(
            final_percentages
        )[::-1]

        sorted_options = [
            business_options[index]
            for index in sorted_indexes
        ]

        sorted_scores = [
            final_percentages[index]
            for index in sorted_indexes
        ]

        best_option_index = int(
            np.argmax(
                final_scores
            )
        )

        best_option = (
            business_options[best_option_index]
        )

        best_score = (
            final_percentages[best_option_index]
        )

        recommendation_label, score_gap, recommendation_message = (
            get_recommendation_strength(
                sorted_scores
            )
        )

        confidence_label = get_decision_confidence(
            st.session_state
            .factor_results["consistency_ratio"]
        )[0]

        sensitivity_result = run_sensitivity_analysis()

        st.subheader(
            "Executive Summary"
        )

        st.markdown(
            f"""
            <div class="app-panel">
                <strong>{best_option}</strong> is the strongest option based on your factor priorities
                and option comparisons. The result should support your business judgment rather than
                replace it.
            </div>
            """,
            unsafe_allow_html=True
        )

        summary_left, summary_middle, summary_right = st.columns(3)

        with summary_left:

            st.metric(
                "Recommended Option",
                best_option
            )

        with summary_middle:

            st.metric(
                "Overall Score",
                f"{best_score:.2f}%"
            )

        with summary_right:

            st.metric(
                "Decision Confidence",
                confidence_label
            )

        st.subheader(
            "Recommended Business Option"
        )

        st.success(
            f"{best_option} is recommended with an overall score of "
            f"{best_score:.2f}%."
        )

        st.write(
            "This score combines the importance of each decision factor "
            "with how well each business option performed under those "
            "factors."
        )

        st.subheader(
            "Decision Confidence"
        )

        st.info(
            f"{recommendation_label}: {recommendation_message} "
            f"The lead over the second-ranked option is "
            f"{score_gap:.2f} percentage points."
        )

        st.subheader(
            "Why This Recommendation was Generated"
        )

        factor_importance_scores = (
            st.session_state
            .factor_results["importance_scores"]
        )

        top_factor_index = int(
            np.argmax(
                factor_importance_scores
            )
        )

        top_factor = (
            st.session_state
            .selected_factors[top_factor_index]
        )

        top_factor_weight = (
            factor_importance_scores[top_factor_index]
        )

        top_factor_option_scores = (
            st.session_state
            .option_results[top_factor]["importance_scores"]
        )

        top_option_under_top_factor_index = int(
            np.argmax(
                top_factor_option_scores
            )
        )

        top_option_under_top_factor = (
            business_options[
                top_option_under_top_factor_index
            ]
        )

        recommended_score_under_top_factor = (
            top_factor_option_scores[best_option_index]
        )

        st.write(
            f"{top_factor} was your most important decision factor "
            f"({top_factor_weight:.2f}% importance)."
        )

        if (
            top_option_under_top_factor_index
            ==
            best_option_index
        ):

            st.write(
                f"{best_option} achieved the strongest performance "
                f"under {top_factor}, with a score of "
                f"{recommended_score_under_top_factor:.2f}%."
            )

            st.write(
                f"Because {top_factor} carried the largest importance "
                "weight, this strong performance had the greatest "
                "influence on the final recommendation."
            )

        else:

            st.write(
                f"{top_option_under_top_factor} achieved the strongest "
                f"performance under {top_factor}. {best_option} scored "
                f"{recommended_score_under_top_factor:.2f}% under that "
                "factor."
            )

            factor_weights = (
                st.session_state
                .factor_results["priority_weights"]
            )

            recommendation_contributions = []

            for factor_index, factor in enumerate(
                st.session_state.selected_factors
            ):

                option_score = (
                    st.session_state
                    .option_results[factor]["priority_weights"][
                        best_option_index
                    ]
                )

                recommendation_contributions.append(
                    factor_weights[factor_index]
                    *
                    option_score
                )

            strongest_support_index = int(
                np.argmax(
                    recommendation_contributions
                )
            )

            strongest_support_factor = (
                st.session_state
                .selected_factors[
                    strongest_support_index
                ]
            )

            strongest_support_score = (
                st.session_state
                .option_results[
                    strongest_support_factor
                ]["importance_scores"][best_option_index]
            )

            st.write(
                f"{best_option} received its strongest weighted support "
                f"from {strongest_support_factor}, where it scored "
                f"{strongest_support_score:.2f}%."
            )

            st.write(
                f"Its combined performance across all factors produced "
                f"the highest overall score of {best_score:.2f}%, even "
                f"though another option led under {top_factor} alone."
            )

        st.subheader(
            "Key Decision Drivers"
        )

        driver_data = scores_dataframe(
            st.session_state.selected_factors,
            st.session_state.factor_results["importance_scores"]
        )

        st.dataframe(
            driver_data,
            use_container_width=True
        )

        influence_label, influence_message = (
            get_factor_influence_feedback(
                st.session_state.selected_factors,
                st.session_state
                .factor_results["importance_scores"]
            )
        )

        st.write(
            f"{influence_label}: {influence_message}"
        )

        st.subheader(
            "Visual Charts"
        )

        factor_chart_data = build_chart_data(
            st.session_state.selected_factors,
            st.session_state.factor_results["importance_scores"],
            "Importance (%)"
        )

        st.write(
            "Factor Importance Scores"
        )

        st.bar_chart(
            factor_chart_data,
            color="#003A86"
        )

        st.write(
            "Final Business Option Scores"
        )

        final_chart_data = build_chart_data(
            business_options,
            final_percentages,
            "Overall Score (%)"
        )

        st.bar_chart(
            final_chart_data,
            color="#FFC222"
        )

        st.subheader(
            "Sensitivity Analysis"
        )

        if sensitivity_result["status"] == "Stable Recommendation":

            st.success(
                "Stable Recommendation"
            )

            st.write(
                "The recommended option did not change when each factor "
                "weight was increased or decreased by 5%. This suggests "
                "the recommendation is stable under small changes in your "
                "priorities."
            )

        else:

            changed_factors = [
                (
                    f"{row['Factor Tested']} "
                    f"({row['Change Applied']})"
                )
                for row in sensitivity_result["changed_cases"]
            ]

            st.warning(
                "Recommendation Changes"
            )

            st.write(
                "The recommended option changed during sensitivity testing. "
                "This means the decision is sensitive to small changes in: "
                f"{', '.join(changed_factors)}."
            )

        st.dataframe(
            pd.DataFrame(
                sensitivity_result["rows"]
            ),
            use_container_width=True,
            hide_index=True
        )

        with st.expander(
            "Detailed Analysis"
        ):

            st.subheader(
                "Overall Business Option Scores"
            )

            st.dataframe(
                scores_dataframe(
                    sorted_options,
                    sorted_scores
                ),
                use_container_width=True
            )

            st.subheader(
                "Option Scores by Factor"
            )

            for factor in st.session_state.selected_factors:

                option_results = (
                    st.session_state.option_results[factor]
                )

                st.write(
                    f"Under {factor}, these scores show which "
                    "business option performed best for that one "
                    "factor only."
                )

                st.dataframe(
                    scores_dataframe(
                        business_options,
                        option_results["importance_scores"]
                    ),
                    use_container_width=True
                )

        with st.expander(
            "Technical Analysis"
        ):

            render_factor_technical_analysis(
                st.session_state.factor_results,
                st.session_state.factor_comparison_matrix,
                st.session_state.selected_factors
            )

            st.subheader(
                "Alternative Comparison Matrices"
            )

            for factor in st.session_state.selected_factors:

                st.write(
                    f"Business option matrix for {factor}"
                )

                st.dataframe(
                    matrix_dataframe(
                        st.session_state.option_matrices[factor],
                        business_options
                    ),
                    use_container_width=True
                )

        st.subheader(
            "Decision Record and Evaluation"
        )

        st.write(
            "These optional fields help identify the decision when exporting results."
        )

        metadata_left, metadata_right = st.columns(2)

        with metadata_left:

            business_name = st.text_input(
                "Business Name (optional)",
                key="export_business_name"
            )

        with metadata_right:

            industry = st.text_input(
                "Industry (optional)",
                key="export_industry"
            )

        st.write(
            "Before downloading the results, please complete this short evaluation."
        )

        understanding = st.radio(
            "Was the recommendation easy to understand?",
            [
                "Very Easy",
                "Easy",
                "Neutral",
                "Difficult",
                "Very Difficult"
            ],
            key="evaluation_understanding"
        )

        reflected_decision = st.radio(
            "Did the recommendation reflect how you normally make business decisions?",
            [
                "Yes",
                "Partially",
                "No"
            ],
            key="evaluation_reflected_decision"
        )

        use_again = st.radio(
            "Would you use this system again?",
            [
                "Yes",
                "Maybe",
                "No"
            ],
            key="evaluation_use_again"
        )

        additional_comments = st.text_area(
            "Additional comments",
            key="evaluation_comments"
        )

        evaluation_responses = {
            "Was the recommendation easy to understand?": understanding,
            "Did the recommendation reflect how you normally make business decisions?": reflected_decision,
            "Would you use this system again?": use_again,
            "Additional comments": additional_comments
        }

        export_csv = build_results_export_csv(
            business_name,
            industry,
            confidence_label,
            best_option,
            sensitivity_result,
            evaluation_responses
        )

        st.download_button(
            "Download Results CSV",
            data=export_csv,
            file_name="ahp_decision_results.csv",
            mime="text/csv"
        )

        st.divider()

        left_column, middle_column, right_column = st.columns(3)

        with left_column:

            if st.button(
                "Review Factor Results"
            ):

                st.session_state.page = (
                    "factor_results"
                )

                st.rerun()

        with middle_column:

            if st.button(
                "Review Option Comparisons"
            ):

                st.session_state.option_factor_index = 0
                st.session_state.option_pair_index = 0
                st.session_state.page = (
                    "option_comparison"
                )

                st.rerun()

        with right_column:

            if st.button(
                "Start New Decision"
            ):

                st.session_state.selected_factors = []
                reset_factor_comparison_state()
                reset_option_state()
                st.session_state.page = (
                    "factor_selection"
                )

                st.rerun()
