import numpy as np


# =========================================================
# AHP DECISION SUPPORT SYSTEM
# =========================================================
#
# GOAL:
# Convert human judgments into priority rankings
# while checking if the judgments are logically consistent.
#
# NOTE:
# We normalize values to create comparable proportions,
# then average rows to derive criteria priority weights.
#
# =========================================================



# =========================================================
# STEP 1:
# DEFINE DECISION FACTORS
# =========================================================

decision_factors = [
    "Cost",
    "Speed",
    "Quality"
]



# =========================================================
# STEP 2:
# DEFINE THE PAIRWISE COMPARISON MATRIX
# =========================================================
#
# RULE:
# Rows are compared against columns.
#
# Example:
#
# matrix[0][1] = 3
#
# Means:
#
# Row 0 is 3x more important than Column 1
#
# =========================================================

comparison_matrix = np.array([

    # Cost comparisons
    [1,   3,   5],

    # Speed comparisons
    [1/3, 1,   2],

    # Quality comparisons
    [1/5, 1/2, 1]

])


print("\n=================================================")
print("ORIGINAL COMPARISON MATRIX")
print("=================================================")

print(comparison_matrix)



# =========================================================
# STEP 3:
# CALCULATE COLUMN TOTALS
# =========================================================
#
# WHY?
#
# We calculate column totals so we can normalize
# the matrix into proportional values.
#
# =========================================================

column_totals = comparison_matrix.sum(axis=0)


print("\n=================================================")
print("COLUMN TOTALS")
print("=================================================")

print(np.round(column_totals, 3))



# =========================================================
# STEP 4:
# NORMALIZE THE MATRIX
# =========================================================
#
# FORMULA:
#
# Normalized Value =
# Original Value / Column Total
#
# WHY?
#
# This converts raw judgment values
# into comparable proportions.
#
# =========================================================

normalized_matrix = comparison_matrix / column_totals


print("\n=================================================")
print("NORMALIZED MATRIX")
print("=================================================")

print(np.round(normalized_matrix, 3))



# =========================================================
# STEP 5:
# CALCULATE CRITERIA PRIORITY WEIGHTS
# =========================================================
#
# METHOD:
#
# Find average value across each row.
#
# axis = 0:
# Move vertically down columns
#
# axis = 1:
# Move horizontally across rows
#
# WHY?
#
# This gives the overall importance weight
# for each decision factor.
#
# =========================================================

priority_weights = normalized_matrix.mean(axis=1)


# Convert decimal weights into percentages
priority_percentages = priority_weights * 100


print("\n=================================================")
print("DECISION FACTOR PRIORITIES")
print("=================================================")

for factor, percentage in zip(
    decision_factors,
    priority_percentages
):

    print(f"{factor}: {percentage:.2f}%")


# =========================================================
# STEP 6:
# CALCULATE WEIGHTED SUM VECTOR
# =========================================================
#
# WHY?
#
# This helps measure judgment consistency.
#
# =========================================================

weighted_sum_vector = np.dot(
    comparison_matrix,
    priority_weights
)


print("\n=================================================")
print("WEIGHTED SUM VECTOR")
print("=================================================")

print(np.round(weighted_sum_vector, 3))



# =========================================================
# STEP 7:
# CALCULATE CONSISTENCY VECTOR
# =========================================================
#
# FORMULA:
#
# weighted_sum_vector / priority_weights
#
# =========================================================

consistency_vector = (
    weighted_sum_vector / priority_weights
)


print("\n=================================================")
print("CONSISTENCY VECTOR")
print("=================================================")

print(np.round(consistency_vector, 3))



# =========================================================
# STEP 8:
# CALCULATE LAMBDA MAX
# =========================================================
#
# WHY?
#
# Lambda Max helps determine
# logical consistency.
#
# =========================================================

lambda_max = consistency_vector.mean()


print("\n=================================================")
print("LAMBDA MAX")
print("=================================================")

print(round(lambda_max, 3))



# =========================================================
# STEP 9:
# CALCULATE CONSISTENCY INDEX (CI)
# =========================================================
#
# FORMULA:
#
# CI = (Lambda Max - n) / (n - 1)
#
# =========================================================

matrix_size = comparison_matrix.shape[0]

consistency_index = (
    (lambda_max - matrix_size)
    /
    (matrix_size - 1)
)


print("\n=================================================")
print("CONSISTENCY INDEX (CI)")
print("=================================================")

print(round(consistency_index, 5))



# =========================================================
# STEP 10:
# RANDOM INDEX (RI)
# =========================================================
#
# RI represents the average inconsistency
# of random human judgments.
#
# These values were developed by Saaty.
#
# =========================================================

random_index_table = {

    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49
}


random_index = random_index_table[matrix_size]


print("\n=================================================")
print("RANDOM INDEX (RI)")
print("=================================================")

print(random_index)



# =========================================================
# STEP 11:
# CALCULATE CONSISTENCY RATIO (CR)
# =========================================================
#
# FORMULA:
#
# CR = CI / RI
#
# INTERPRETATION:
#
# CR <= 0.10
# = acceptable consistency
#
# =========================================================

consistency_ratio = (
    consistency_index / random_index
)


print("\n=================================================")
print("CONSISTENCY RATIO (CR)")
print("=================================================")

print(round(consistency_ratio, 5))



# =========================================================
# STEP 12:
# FINAL CONSISTENCY DECISION
# =========================================================

print("\n=================================================")
print("FINAL RESULT")
print("=================================================")

if consistency_ratio <= 0.10:

    print("Judgments are CONSISTENT")

else:

    print("Judgments are NOT CONSISTENT")