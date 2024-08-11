import numpy as np

# Given arrays with non-integer elements
array1 = np.array([1.2, 5.4, 7.1, 3.3])
array2 = np.array([3, 5, 8, 3])

# Get the indices that would sort array1
sorted_indices = np.argsort(array1)
print(sorted_indices)
# Use these indices to reorder array2
sorted_array2 = array2[sorted_indices]

print(sorted_array2)