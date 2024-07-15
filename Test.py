import numpy as np
import math 

def calculate_r_phi(X,Y,x,y):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)+90+360)%360

    if angle > 180:
        angle = -(360-angle)
    
    return distance, angle 

def pol2cart(X,Y,d, phi):

    x = X + d * np.sin(math.radians(phi))
    y = Y - d * np.cos(math.radians(phi))
    return(int(x), int(y))

ship_x = -133.382
ship_y = -112.456

x = -18.597
y = -164.24

r, phi = calculate_r_phi(ship_x,ship_y,x,y)
print(r,phi)
x,y = pol2cart(ship_x,ship_y,r,phi)
print(x,y)