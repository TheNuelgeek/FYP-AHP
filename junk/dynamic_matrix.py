import numpy as np


# =========================================================
# STEP 1:
# DEFINE DECISION FACTORS
# =========================================================

decision_factors = [
    "Cost",
    "Speed",
    "Quality"
]


# Number of decision factors
number_of_factors = len(decision_factors)


# =========================================================
# STEP 2:
# CREATE EMPTY MATRIX
# =========================================================
#
# np.ones creates a matrix filled with 1s.
#
# Example for 3x3:
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
# We only ask for upper triangle comparisons.
#
# Example:
#
# Cost vs Speed
# Cost vs Quality
# Speed vs Quality
#
# =========================================================

for row in range(number_of_factors):

    for column in range(row + 1, number_of_factors):

        row_factor = decision_factors[row]

        column_factor = decision_factors[column]

        print("\n-----------------------------------")
        print(f"{row_factor} vs {column_factor}")
        print("-----------------------------------")

        print(f"""
How important is {row_factor}
compared to {column_factor}?

Saaty Scale:
1  = Equal Importance
3  = Moderate Importance
5  = Strong Importance
7  = Very Strong Importance
9  = Extreme Importance
""")

        user_input = float(input("Enter value: "))


        # Store direct judgment
        comparison_matrix[row][column] = user_input


        # Automatically store reciprocal value
        comparison_matrix[column][row] = 1 / user_input


# =========================================================
# STEP 4:
# DISPLAY FINAL MATRIX
# =========================================================

print("\n=================================================")
print("FINAL COMPARISON MATRIX")
print("=================================================")

print(np.round(comparison_matrix, 3))