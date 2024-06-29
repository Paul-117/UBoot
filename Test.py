import math
import numpy as np



def calculate_r_phi(X,Y,Phi,x,y,u):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    delta_distance = u
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)+90-Phi+360)%360
    #angle = (180 / math.pi) * math.atan2(-dir_y, dir_x)+90-Phi
    print(angle)
    if angle > 180:
        angle = -(360-angle)
    
    #delta_angle = math.asin(u/distance)

    return angle

X = 0
Y = 0 
x = -50
y = -50
Phi = 0

a = calculate_r_phi(X,Y,Phi,x,y, 100)
print(a)
#b = np.arange(0,361,10)

#for i in b:
#    print(i, calculate_r_phi2(X,Y,i,x,y, 100))
