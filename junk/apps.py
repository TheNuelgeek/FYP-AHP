elif (
    st.session_state.page
    ==
    "factor_comparison"
):

    st.title(
        "Factor Comparison"
    )

    st.write(
        """
        Compare the importance of the
        selected decision factors.
        """
    )

    st.write(
        "Selected Factors:"
    )

    for factor in (
        st.session_state.selected_factors
    ):

        st.write(
            f"• {factor}"
        )

    st.divider()

    first_factor = (
        st.session_state.selected_factors[0]
    )

    second_factor = (
        st.session_state.selected_factors[1]
    )

    st.subheader(
        f"{first_factor} vs {second_factor}"
    )

    comparison_choice = st.radio(

        "Which factor is more important?",

        [
            f"{first_factor} Extreme",
            f"{first_factor} Very Strong",
            f"{first_factor} Strong",
            f"{first_factor} Moderate",
            "Equal Importance",
            f"{second_factor} Moderate",
            f"{second_factor} Strong",
            f"{second_factor} Very Strong",
            f"{second_factor} Extreme"
        ]
    )

    st.info(
        f"Selected: {comparison_choice}"
    )

    st.divider()

    if st.button(
        "Back to Factor Selection"
    ):

        st.session_state.page = (
            "factor_selection"
        )

        st.rerun()