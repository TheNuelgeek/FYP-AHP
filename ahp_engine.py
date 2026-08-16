import numpy as np
from constants import (
    SUGGESTED_FACTORS,
    RANDOM_INDEX_TABLE
)


# =========================================================
# AHP DECISION SUPPORT SYSTEM
# =========================================================
#
# GOAL:
# Convert human judgments into importance scores
# while checking logical consistency.
#
# =========================================================


# =========================================================
# HELPER FUNCTION:
# VALID YES/NO INPUT
# =========================================================

def get_valid_yes_no(prompt):

    while True:

        user_input = input(prompt).strip().lower()

        if user_input in ["yes", "no"]:

            return user_input

        print("""
Invalid input.
Please type 'yes' or 'no'.
""")


# =========================================================
# HELPER FUNCTION:
# VALID MENU SELECTION
# =========================================================

def get_valid_menu_choice(prompt, valid_choices):

    while True:

        user_input = input(prompt).strip()

        if user_input in valid_choices:

            return user_input

        print(f"""
Invalid selection.

Choose from:
{", ".join(valid_choices)}
""")


# =========================================================
# HELPER FUNCTION:
# VALID SAATY SCALE INPUT
# =========================================================

def get_valid_saaty_value():

    valid_values = [

        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
    ]

    while True:

        user_input = input(
            "Enter importance value: "
        ).strip()


        try:

            numeric_value = int(user_input)

            if numeric_value in valid_values:

                return numeric_value

            else:

                print("""
Invalid Saaty value.

Allowed values:

1 to 9

1 = Equal Importance
3 = Moderate Importance
5 = Strong Importance
7 = Very Strong Importance
9 = Extreme Importance

2, 4, 6 and 8 represent
intermediate judgments.
""")

        except ValueError:

            print("""
Invalid input.
Enter a number only.
""")


# =========================================================
# HELPER FUNCTION:
# VALID FACTOR SELECTION
# =========================================================

def get_valid_factor_selection(max_number):

    while True:

        selection = input(
            "\nYour selection: "
        ).strip()


        values = selection.split(",")

        cleaned_values = []


        valid = True

        for value in values:

            value = value.strip()

            if not value.isdigit():

                valid = False
                break


            number = int(value)

            if number < 1 or number > max_number:

                valid = False
                break


            cleaned_values.append(number)


        if valid and len(cleaned_values) > 0:

            return cleaned_values


        print("""
Invalid selection.

Example:
1,3,5
""")
        
# =========================================================
# STEP 1:
# DEFINE DECISION FACTORS
# =========================================================
#
# GOAL:
#
# Help users select operational factors
# for evaluating business decisions.
#
# The system provides suggested factors
# based on common SME operational priorities.
#
# Users may:
# - select suggested factors
# - add custom factors
# - combine both approaches
#
# =========================================================


# =========================================================
# SUGGESTED DECISION FACTORS
# =========================================================

suggested_factors = (
    SUGGESTED_FACTORS.copy()
)


decision_factors = []


# =========================================================
# DISPLAY SUGGESTED FACTORS
# =========================================================

print("\n=================================================")
print("DECISION FACTOR SELECTION")
print("=================================================")

print("""
Suggested decision factors are based on
common SME operational priorities.

You may:
- select from the suggested list
- add your own custom factors
- combine both approaches
""")


# =========================================================
# SHOW FACTOR LIST
# =========================================================

def display_factor_list():

    print("\nSuggested Factors:\n")

    for index, factor in enumerate(

        suggested_factors,
        start=1
    ):

        print(f"[{index}] {factor}")


display_factor_list()


# =========================================================
# ADD CUSTOM FACTORS
# =========================================================

while True:

    add_custom = get_valid_yes_no("""

Would you like to add a custom factor?
(yes/no): 
""")


    if add_custom == "yes":

        custom_factor = input(
            "\nEnter custom factor name: "
        ).strip()


        # =============================================
        # STANDARDIZE INPUT
        # =============================================

        custom_factor = custom_factor.title()


        # =============================================
        # CHECK FOR DUPLICATES
        # =============================================

        existing_factors = [

            factor.lower()
            for factor in suggested_factors
        ]


        if custom_factor.lower() in existing_factors:

            print("""
That factor already exists in the suggested list.
""")

        else:

            suggested_factors.append(
                custom_factor
            )

            print(f"""
'{custom_factor}' added successfully.
""")


            # =========================================
            # SHOW UPDATED LIST
            # =========================================

            display_factor_list()


    elif add_custom == "no":

        break

# =========================================================
# SELECT FINAL DECISION FACTORS
# =========================================================

print("""
Enter the numbers of the factors you want to use.

Example:
1,3,5
""")


selected_numbers = get_valid_factor_selection(
    len(suggested_factors)
)


# =========================================================
# BUILD FINAL FACTOR LIST
# =========================================================

for number in selected_numbers:

    factor_index = number - 1


    if (
        factor_index >= 0
        and
        factor_index < len(suggested_factors)
    ):

        selected_factor = (
            suggested_factors[factor_index]
        )

        decision_factors.append(
            selected_factor
        )


# =========================================================
# REMOVE DUPLICATES
# =========================================================

decision_factors = list(
    dict.fromkeys(decision_factors)
)

# =========================================================
# MINIMUM FACTOR CHECK
# =========================================================

if len(decision_factors) < 2:

    print("""
At least TWO decision factors are required
for comparison analysis.
""")

    exit()


# =========================================================
# DISPLAY FINAL FACTORS
# =========================================================

print("\n=================================================")
print("SELECTED DECISION FACTORS")
print("=================================================")

for factor in decision_factors:

    print(f"- {factor}")


# =========================================================
# TOTAL NUMBER OF FACTORS
# =========================================================

number_of_factors = len(
    decision_factors
)



# =========================================================
# STEP 2:
# CREATE EMPTY COMPARISON MATRIX
# =========================================================
#
# np.ones creates a matrix filled with 1s.
#
# Example:
#
# [
#   [1, 1, 1],
#   [1, 1, 1],
#   [1, 1, 1]
# ]
#
# =========================================================

comparison_matrix = np.ones(
    (number_of_factors, number_of_factors)
)



# =========================================================
# STEP 3:
# COLLECT USER JUDGMENTS
# =========================================================
#
# PROCESS:
#
# 1. User selects which factor is more important
# 2. User selects intensity of importance
#
# This reduces cognitive confusion
# during pairwise comparisons.
#
# =========================================================


# Store all comparison decisions
comparison_history = []


for row in range(number_of_factors):

    for column in range(row + 1, number_of_factors):

        first_factor = decision_factors[row]

        second_factor = decision_factors[column]

        print("\n=================================================")
        print("DIRECT COMPARISON")
        print("=================================================")

        print(f"""
Which factor is MORE important?

1. {first_factor}
2. {second_factor}
""")

        more_important_choice = (
    get_valid_menu_choice(
        "Select option (1 or 2): ",
        ["1", "2"]
    )
)


        print(f"""
How much more important is it?

Saaty Scale:
1  = Equal Importance
3  = Moderate Importance
5  = Strong Importance
7  = Very Strong Importance
9  = Extreme Importance
""")

        importance_value = get_valid_saaty_value()


        # =================================================
        # CASE 1:
        # First factor is more important
        # =================================================

        if more_important_choice == "1":

            comparison_matrix[row][column] = (
                importance_value
            )

            comparison_matrix[column][row] = (
                1 / importance_value
            )

            selected_factor = first_factor


        # =================================================
        # CASE 2:
        # Second factor is more important
        # =================================================

        elif more_important_choice == "2":

            comparison_matrix[row][column] = (
                1 / importance_value
            )

            comparison_matrix[column][row] = (
                importance_value
            )

            selected_factor = second_factor


        # =================================================
        # DETERMINE WINNER AND LOSER
        # =================================================

        if selected_factor == first_factor:

            winner = first_factor
            loser = second_factor

        elif selected_factor == second_factor:

            winner = second_factor
            loser = first_factor

        else:

            winner = "Equal Importance"
            loser = "Equal Importance"


        # =================================================
        # STORE COMPARISON HISTORY
        # =================================================

        comparison_history.append({

            "factor_a": first_factor,

            "factor_b": second_factor,

            "winner": winner,

            "loser": loser,

            "importance": importance_value
        })

# =========================================================
# STEP 4:
# DISPLAY COMPARISON MATRIX
# =========================================================

print("\n=================================================")
print("COMPARISON TABLE")
print("=================================================")

print(np.round(comparison_matrix, 3))



# =========================================================
# STEP 5:
# CALCULATE COLUMN TOTALS
# =========================================================

column_totals = comparison_matrix.sum(axis=0)


print("\n=================================================")
print("COLUMN TOTALS")
print("=================================================")

print(np.round(column_totals, 3))



# =========================================================
# STEP 6:
# NORMALIZE MATRIX
# =========================================================
#
# Formula:
#
# Normalized Value =
# Original Value / Column Total
#
# =========================================================

normalized_matrix = (
    comparison_matrix / column_totals
)


print("\n=================================================")
print("NORMALIZED MATRIX")
print("=================================================")

print(np.round(normalized_matrix, 3))



# =========================================================
# STEP 7:
# CALCULATE IMPORTANCE SCORES
# =========================================================
#
# We average each row
# to derive importance weights.
#
# axis = 1:
# move horizontally across rows
#
# =========================================================

priority_weights = (
    normalized_matrix.mean(axis=1)
)


# Convert to percentages
importance_scores = (
    priority_weights * 100
)


print("\n=================================================")
print("IMPORTANCE SCORES")
print("=================================================")

for factor, score in zip(
    decision_factors,
    importance_scores
):

    print(f"{factor}: {score:.2f}%")



# =========================================================
# STEP 8:
# CALCULATE WEIGHTED SUM VECTOR
# =========================================================

weighted_sum_vector = np.dot(
    comparison_matrix,
    priority_weights
)

# =========================================================
# STEP 9:
# DISPLAY DECISION REVIEW SUMMARY
# =========================================================

print("\n=================================================")
print("DECISION REVIEW SUMMARY")
print("=================================================")


# Convert numeric values into readable labels
def get_importance_label(value):

    if value == 1:
        return "EQUALLY important"

    elif value == 3:
        return "MODERATELY more important"

    elif value == 5:
        return "STRONGLY more important"

    elif value == 7:
        return "VERY STRONGLY more important"

    elif value == 9:
        return "EXTREMELY more important"

    else:
        return f"{value}x more important"


# Display comparison history
for comparison in comparison_history:

    factor_a = comparison["factor_a"]

    factor_b = comparison["factor_b"]

    winner = comparison["winner"]

    loser = comparison["loser"]

    importance = comparison["importance"]

    importance_label = (
        get_importance_label(importance)
    )

    if winner == "Equal Importance":

        print(
            f"- {factor_a} and {factor_b} "
            f"were rated equally important."
        )

    else:

        print(
            f"- {winner} was rated "
            f"{importance_label} "
            f"than {loser}."
        )


# =========================================================
# STEP 10: - Deleted
# COMPARISON TENSION REVIEW
# =========================================================



# =========================================================
# STEP 11:
# CALCULATE CONSISTENCY VECTOR
# =========================================================

consistency_vector = (
    weighted_sum_vector / priority_weights
)



# =========================================================
# STEP 12:
# CALCULATE LAMBDA MAX
# =========================================================

lambda_max = (
    consistency_vector.mean()
)



# =========================================================
# STEP 13:
# CALCULATE CONSISTENCY INDEX (CI)
# =========================================================

matrix_size = comparison_matrix.shape[0]

consistency_index = (
    (lambda_max - matrix_size)
    /
    (matrix_size - 1)
)



# =========================================================
# STEP 14:
# RANDOM INDEX TABLE
# =========================================================

random_index = RANDOM_INDEX_TABLE.get(
    matrix_size,
    1.49
)


# =========================================================
# STEP 15:
# CALCULATE CONSISTENCY RATIO (CR)
# =========================================================

if random_index == 0:

    consistency_ratio = 0

else:

    consistency_ratio = (
        consistency_index / random_index
    )



# =========================================================
# STEP 16:
# DISPLAY DECISION CONSISTENCY STATUS
# =========================================================

print("\n=================================================")
print("DECISION CONSISTENCY")
print("=================================================")

print(
    f"Consistency Score: "
    f"{consistency_ratio:.5f}"
)

if matrix_size <= 2:

    print("""
Consistency analysis is automatically valid
for two-factor comparisons.
""")


    
# =========================================================
# STEP 17:
# PLAIN-LANGUAGE INCONSISTENCY EXPLANATION
# =========================================================

def build_implied_ladder(matrix, factors, weights):
    """
    Uses the least important factor (lowest priority weight)
    as the anchor point at position 1.
    Expresses all other factors relative to that anchor
    using the comparison matrix, then scales to 1-9.
    """
    anchor_index = int(np.argmin(weights))
    anchor = factors[anchor_index]

    ladder = {}
    for i in range(len(factors)):
        ratio = matrix[i][anchor_index]
        ladder[factors[i]] = ratio

    max_val = max(ladder.values())
    scale_factor = 9 / max_val

    scaled_ladder = {
        f: max(1.0, round(v * scale_factor, 1))
        for f, v in ladder.items()
    }

    return anchor, scaled_ladder


def find_top_conflicts(matrix, factors, ladder, top_n=2):
    """
    Loops over all unique pairs.
    For each pair, compares where both factors sit
    on the ladder versus what the user stated directly.
    Returns the top_n most conflicted pairs by gap size.
    """
    n = len(factors)
    conflicts = []
    seen_pairs = set()

    for i in range(n):
        for k in range(n):
            if i == k:
                continue

            pair = tuple(sorted([i, k]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            stated = matrix[i][k]
            implied = ladder[factors[i]] / ladder[factors[k]]

            if stated == 0 or implied == 0:
                continue

            gap = max(implied / stated, stated / implied)

            conflicts.append({
                "factor_high_on_ladder": (
                    factors[i]
                    if ladder[factors[i]] > ladder[factors[k]]
                    else factors[k]
                ),
                "factor_low_on_ladder": (
                    factors[k]
                    if ladder[factors[i]] > ladder[factors[k]]
                    else factors[i]
                ),
                "ladder_high_score": max(
                    ladder[factors[i]], ladder[factors[k]]
                ),
                "ladder_low_score": min(
                    ladder[factors[i]], ladder[factors[k]]
                ),
                "stated_winner": (
                    factors[i] if stated >= 1 else factors[k]
                ),
                "stated_loser": (
                    factors[k] if stated >= 1 else factors[i]
                ),
                "stated_value": (
                    stated if stated >= 1 else 1 / stated
                ),
                "gap": gap
            })

    conflicts.sort(key=lambda x: x["gap"], reverse=True)
    return conflicts[:top_n]


# =========================================================
# CONSISTENT — simple confirmation, nothing more
# =========================================================

if consistency_ratio <= 0.10:

    print("\n=================================================")
    print("DECISION CONSISTENCY")
    print("=================================================")
    print("""
Your comparisons are consistent.

Your importance scores are reliable
and ready to use.
""")


# =========================================================
# INCONSISTENT — diagnose and explain
# =========================================================

else:

    anchor, ladder = build_implied_ladder(
        comparison_matrix,
        decision_factors,
        priority_weights
    )

    # 3 factors → show 1 conflict
    # 4+ factors → show top 2
    top_n = 1 if number_of_factors <= 3 else 2

    conflicts = find_top_conflicts(
        comparison_matrix,
        decision_factors,
        ladder,
        top_n=top_n
    )

    print("\n=================================================")
    print("WHERE YOUR COMPARISONS CONFLICT")
    print("=================================================")

    # --- Ladder display ---
    print("""
          Based on your answers, here is the relative
          position of your decision factors:
          """)

    sorted_ladder = sorted(
        ladder.items(),
        key=lambda x: x[1]
    )

    for factor, score in sorted_ladder:
        bar = "█" * int(score)
        anchor_note = "  <- least important" if factor == anchor else ""
        print(f"  {factor:<14} {score:>4}  {bar}{anchor_note}")

    # --- Conflict display ---
    for idx, conflict in enumerate(conflicts, 1):

        high       = conflict["factor_high_on_ladder"]
        low        = conflict["factor_low_on_ladder"]
        h_score    = conflict["ladder_high_score"]
        l_score    = conflict["ladder_low_score"]
        winner     = conflict["stated_winner"]
        loser      = conflict["stated_loser"]
        stated_val = conflict["stated_value"]

        direction_conflict = (high != winner)

        label = (
            f"CONFLICT {idx}"
            if len(conflicts) > 1
            else "THE CONFLICT"
        )

        # Only show a block if direction actually conflicts
        # Intensity-only mismatches are skipped silently

        if direction_conflict:

            print(f"""
-------------------------------------------------
{label}
-------------------------------------------------

  Your scale places {high} ({h_score}) above
  {low} ({l_score}) — meaning {high} came out
  more important overall.

  But when you compared them directly, you said
  {winner} is {stated_val:.0f}x more important than {loser}.

  That is the conflict.
  One answer says {high} wins.
  The other says {winner} wins.

  -> Go back to your {high} vs {low} comparison.
     Decide which one truly matters more to your
     business, then adjust that rating.
""")


    # =====================================================
    # AFTER THE LOOP:
    # If no direction conflicts were found at all,
    # confirm rankings are usable
    # =====================================================

    direction_conflicts_found = any(
        c["factor_high_on_ladder"] != c["stated_winner"]
        for c in conflicts
    )

    if not direction_conflicts_found:

        print("""
Your rankings are consistent in direction.
You can proceed with your results.
""")
            
# =========================================================
# STEP 18:
# BUSINESS OPTION EVALUATION
# =========================================================


# =========================================================
# BUSINESS OPTION SETUP
# =========================================================

print("\n=================================================")
print("BUSINESS OPTION SETUP")
print("=================================================")

print("""
Business options are the alternatives
you want the system to evaluate.

Examples:
- Open New Branch
- Invest in Marketing
- Hire Sales Staff

Recommended:
2 to 5 business options
""")


while True:

    try:

        number_of_options = int(
            input(
                "\nHow many business options would you like to compare? "
            )
        )

        if 2 <= number_of_options <= 5:

            break

        print("""
Please enter a number between 2 and 5.
""")

    except ValueError:

        print("""
Invalid input.
Please enter a number only.
""")


# =========================================================
# COLLECT BUSINESS OPTIONS
# =========================================================

business_options = []


for option_number in range(
    1,
    number_of_options + 1
):

    while True:

        option_name = input(
            f"\nEnter Business Option {option_number}: "
        ).strip()


        if option_name == "":

            print("""
Business option cannot be empty.
""")

        elif option_name.lower() in [

            option.lower()
            for option in business_options

        ]:

            print("""
That business option already exists.
Enter a different option.
""")

        else:

            business_options.append(
                option_name
            )

            break


print("\n=================================================")
print("BUSINESS OPTIONS")
print("=================================================")

for option in business_options:

    print(f"- {option}")

# =========================================================
# STORAGE:
# SAVE OPTION SCORES FOR EACH FACTOR
# =========================================================

all_option_scores = {}


number_of_options = len(
    business_options
)


# =========================================================
# EVALUATE OPTIONS UNDER EACH FACTOR
# =========================================================

for selected_factor in decision_factors:


    print("\n=================================================")
    print("BUSINESS OPTION EVALUATION")
    print("=================================================")

    print(
        f"Business options will be evaluated using: "
        f"{selected_factor}"
    )


    # =====================================================
    # CREATE OPTION COMPARISON MATRIX
    # =====================================================

    option_matrix = np.ones(
        (number_of_options, number_of_options)
    )


    # =====================================================
    # COLLECT OPTION COMPARISONS
    # =====================================================

    for row in range(number_of_options):

        for column in range(row + 1, number_of_options):

            first_option = business_options[row]

            second_option = business_options[column]


            print("\n=================================================")
            print("BUSINESS OPTION COMPARISON")
            print("=================================================")


            # =================================================
            # QUESTION 1:
            # Which option is better for this factor?
            # =================================================

            print(f"""
Thinking about {selected_factor} only —
which of these two options is better for your business?

1. {first_option}
2. {second_option}
""")

            better_option = get_valid_menu_choice(
                "Select option (1 or 2): ",
                ["1", "2"]
            )


            # =================================================
            # DETERMINE SELECTED OPTION
            # =================================================

            if better_option == "1":

                selected_option = first_option

                not_selected_option = second_option

            else:

                selected_option = second_option

                not_selected_option = first_option


            # =================================================
            # QUESTION 2:
            # How much better?
            # =================================================

            print(f"""
How much better is {selected_option}
compared to {not_selected_option}?

Saaty Scale:
1  = No real difference
3  = Somewhat better
5  = Clearly better
7  = Much better
9  = Incomparably better
""")


            importance_value = get_valid_saaty_value()


            # =================================================
            # OPTION 1 IS BETTER
            # =================================================

            if better_option == "1":

                option_matrix[row][column] = (
                    importance_value
                )

                option_matrix[column][row] = (
                    1 / importance_value
                )


            # =================================================
            # OPTION 2 IS BETTER
            # =================================================

            elif better_option == "2":

                option_matrix[row][column] = (
                    1 / importance_value
                )

                option_matrix[column][row] = (
                    importance_value
                )


    # =====================================================
    # NORMALIZE OPTION MATRIX
    # =====================================================

    option_column_totals = (
        option_matrix.sum(axis=0)
    )


    normalized_option_matrix = (
        option_matrix / option_column_totals
    )


    # =====================================================
    # CALCULATE OPTION SCORES
    # =====================================================

    option_priority_scores = (
        normalized_option_matrix.mean(axis=1)
    )


    # =====================================================
    # STORE SCORES FOR THIS FACTOR
    # =====================================================

    all_option_scores[selected_factor] = (
        option_priority_scores
    )


    # =====================================================
    # DISPLAY RESULTS FOR THIS FACTOR
    # =====================================================

    print("\n=================================================")
    print(f"RESULTS FOR: {selected_factor}")
    print("=================================================")


    for option, score in zip(

        business_options,
        option_priority_scores * 100
    ):

        print(f"{option}: {score:.2f}%")


# =========================================================
# STEP 19:
# FINAL WEIGHTED SYNTHESIS
# =========================================================

final_scores = np.zeros(
    number_of_options
)


for factor_index, factor in enumerate(
    decision_factors
):

    factor_weight = (
        priority_weights[factor_index]
    )


    option_scores = (
        all_option_scores[factor]
    )


    final_scores += (
        factor_weight * option_scores
    )


# =========================================================
# CONVERT FINAL SCORES TO PERCENTAGES
# =========================================================

final_percentages = (
    final_scores * 100
)


# =========================================================
# STEP 20:
# FINAL BUSINESS RECOMMENDATION
# =========================================================

print("\n=================================================")
print("FINAL BUSINESS RECOMMENDATION")
print("=================================================")


for option, score in zip(

    business_options,
    final_percentages
):

    print(f"{option}: {score:.2f}%")


# =========================================================
# FIND BEST OPTION
# =========================================================

best_option_index = np.argmax(
    final_scores
)


best_option = (
    business_options[best_option_index]
)


print("\n=================================================")
print("RECOMMENDED BUSINESS OPTION")
print("=================================================")

print(f"\n{best_option}")