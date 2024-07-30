import numpy as np
import math 
import matplotlib.pyplot as plt

def calculate_r_phi(X,Y,x,y):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)+90+360)%360

    if angle > 180:
        angle = -(360-angle)
    
    return distance, angle 

print(calculate_r_phi(0,0,10,10))

