import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math

coordinates = (1000,000)

def retrieve_xy(coordinates):
    
    r = np.sqrt(coordinates[0]**2+coordinates[1]**2)
    print(r)
    sigma = 100+0.02*r
    print(sigma)
    x = np.random.normal(loc=coordinates[0], scale=100, size=None)
    y = np.random.normal(loc=coordinates[0], scale=100, size=None)

b = retrieve_xy(coordinates)