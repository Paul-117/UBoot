import numpy as np
import math 
import matplotlib.pyplot as plt

array1 = [1, 7, 5, 3]
array2 = [6, 7, 9, 5]

# Get the sorted indices of array1
sorted_indices = sorted(range(len(array1)), key=lambda i: array1[i], reverse=True)

# Rearrange array1 and array2 according to the sorted order of array1
sorted_array1 = [array1[i] for i in sorted_indices]
sorted_array2 = [array2[i] for i in sorted_indices]

# Output the resulting pairs

print(sorted_array1,sorted_array2)