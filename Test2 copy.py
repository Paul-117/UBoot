import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math


x_range = 100
x_pixels = 500
X = np.linspace(0,x_range,x_pixels)
scale = int(x_pixels/x_range)

# Grundsignal auf dass modulation addiert wird 
Y = np.zeros(x_pixels)

def add_Gaussian(X,Y,x,I,sigma):

    Y += I*stats.norm.pdf(X, x, sigma)
    
    return Y

def add_multiple_Gaussians(X,Y,x,sigma,n):
    
    max_I = np.max(Y)

    i = 0 
    while i < n:
        I = np.random.uniform(0.1,2)* max_I
        sigma_local = np.random.uniform(sigma/2,5*sigma)
        x = np.random.normal(1,1,x_pixels)
        add_Gaussian(X,Y,x,I,sigma_local)
        print(x,I,sigma_local)
        i += 1 


def add_Noise(Y,I):

    Y += np.random.normal(0,I,x_pixels)
    print(np.random.normal(I,1,x_pixels))



x_d = 50 # coordinate in length scale 

#add_Noise(Y,0.001)



print(np.random.normal(1,1,1))