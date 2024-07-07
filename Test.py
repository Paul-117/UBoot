import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import keyboard  # using module keyboard
from matplotlib.animation import FuncAnimation

from scipy.optimize import curve_fit 
import matplotlib.pyplot as mpl 

import time, threading
import socket
import json
import time
import keyboard
import numpy as np


def calculate_r_phi(X,Y,Phi,x,y):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)-Phi+360)%360

    if angle > 180:
        angle = -(360-angle)
    

    return distance, angle

def pol2cart(X,Y,d, phi):

    x = X + d * np.sin(math.radians(phi))
    y = Y + d * np.cos(math.radians(phi))
    return x, y


a = [-10,0,10]
b = [-10,0,10]
X = 0 
Y = 0 

'''for i in a:
    for j in b:
        d,phi = calculate_r_phi(X,Y,0,i,j)
        plt.scatter(i,j, color = "red")
        x,y = pol2cart(X,Y,d,phi)
        plt.scatter(x,y, color = "blue")
        

plt.show()'''
x = 0
y = -10
d,phi = calculate_r_phi(X,Y,0,x,y)
print(d,phi)
x,y = pol2cart(X,Y,d,phi)
print(x,y)
print(np.sin(math.radians(-90)))