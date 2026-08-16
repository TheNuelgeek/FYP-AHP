import numpy as np

# axis = 0: Coloumn
# axis = 1: Row

matrix = np.array([
    [1, 2],
    [3, 4]
])

print(matrix)

print(matrix.sum(axis=0))
print(matrix.sum(axis=1))

print(matrix.mean(axis=0))
print(matrix.mean(axis=1))

print(matrix.shape)
print(matrix.shape[0])
print(matrix.shape[0])