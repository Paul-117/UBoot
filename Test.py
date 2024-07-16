import numpy as np
import math 
import matplotlib.pyplot as plt

Above_Threashold_Regions = [[1,2,3],[8,9,10,11,12]]
print(Above_Threashold_Regions[0])
X = np.arange(100)
Y = np.zeros(100)
d = 100 

def fuck_d(d):
    delta_d = d*0.1
    d_fucked = d + np.random.uniform(-delta_d, delta_d)

    return d_fucked

for region in Above_Threashold_Regions:
    d_fucked = fuck_d(d)
    Y[region] += d_fucked + np.random.normal(0,d*0.1,len(Y[region]))

    d_retrieved = np.mean(Y[region])
    print(d_retrieved)


plt.plot(X,Y)
plt.show()

