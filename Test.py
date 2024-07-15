import numpy as np

a = np.arange(10)
b = np.arange(20,30)
c = np.append(a,b)
print(np.gradient(c))