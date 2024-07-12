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

def get_game_state():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        command = json.dumps({"type": "get","ID": "Sensorium"}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        print(data)
        game_state = json.loads(data.decode('utf-8'))
        #print(f"Current game state: {game_state}")
        print("connection closed")
        #s.close()
        return game_state

def update_game_state(new_state):
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to Server")
        command = json.dumps({"type": "update","ID": "Sensorium", "data": new_state}).encode('utf-8')
        s.sendall(command)
        print("Data sent")
        #data = s.recv(1024)
        print("Data recieved -->  connection closed")
        #s.close()
        
        #print(data.decode('utf-8'))

def retrieve_xy(x_ship,X,y_ship,Y):
    # Achtung funktion ist auf 1000m Reichweite ausgelegt 
    
    x_relative = X-x_ship
    y_relative = Y-y_ship
    r = np.sqrt(x_relative**2+y_relative**2)
    sigma = 0.05*r
    x = np.random.normal(loc=X, scale=sigma, size=None)
    y = np.random.normal(loc=Y, scale=sigma, size=None)
    print(r,x,y,sigma*5)
    return x,y,sigma*2

#r = np.sqrt(coordinates[0]**2+coordinates[1]**2)

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
    return(x, y)
class Signal:
  
    def __init__(self,name,x,r):

        if name =="distance":
            self.X = 500
        if name == "phi": #später statt von 0-360 0 in die mitte und +-180 hnter dem schiff ist das ende des sensors 

            self.X = 360
        self.name = name
        self.Y = np.zeros(self.X)
        self.Y_stack = np.zeros(self.X)
        self.Y_mean = np.zeros(self.X)
        self.x = x
        self.r = r
        self.Threashold = 0
        self.Average_Spectra = 1
        self.Noise = 0.1
        self.num_of_Gaussians = 3
        self.I = 0
        self.Sigma = 0
        self.x_retrieve_start = 0
        self.x_retrieved = None
        self.x_retrieve_end = 0 
        self.x_retrieved_uncertainty = 0
        # Plotting
        self.fig, self.ax = plt.subplots(figsize = (5,4))
        if self.name == "phi":
             self.line, = self.ax.plot(np.arange(-self.X/2, +self.X/2), self.Y_mean,color='black')
        else:
             self.line, = self.ax.plot(np.arange(0, self.X), self.Y_mean,color='black')
        self.threshold_line_h = self.ax.axhline(self.Threashold, color='red', linestyle='--')
        self.threshold_line_vl = self.ax.axvline(self.x_retrieve_start, color="red")
        self.threshold_line_vr = self.ax.axvline(self.x_retrieve_end, color="red")
        self.text_x_retrieved = self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, fontsize=12)
        self.text_average_spectra = self.ax.text(0.1, 0.85, "", transform=self.ax.transAxes, fontsize=12)
        self.ax.set_ylim(-0.5, 3)
        
        # Calculations
        self.get_I()
        self.get_Sigma()
        print(self.I,self.Sigma)
    
        
        

    def get_I(self):

        if self.r < 500:
            self.I = 2#-self.r*0.001*self.Noise+ 10*self.Noise
        else:
            self.I = 0 

    def get_Sigma(self):
        
        self.Sigma = 0.05*self.r 

    def reset_Y(self):
        self.Y = np.zeros(self.X)

    def add_Noise(self):

        self.Y += np.random.normal(0,self.Noise,self.X)

    def add_Gaussian(self,X,x,I,sigma):

        Y = I*(2.5*sigma)*stats.norm.pdf(X, x, sigma)

        return Y

    def add_multiple_Gaussians(self):
    
        Y_stack = np.zeros(self.X)
        i = 0 
        while i < self.num_of_Gaussians:
            I_local = np.random.uniform(0.1,1)* self.I
            sigma_local = np.random.uniform(0.1*self.Sigma,0.3*self.Sigma)
            x_local = np.random.normal(self.x,self.Sigma*1.5)
            if self.name == "phi":
                Y_local = self.add_Gaussian(np.arange(-self.X/2, self.X/2),x_local,I_local,sigma_local)
            else:
                Y_local = self.add_Gaussian(np.arange(self.X),x_local,I_local,sigma_local)
            Y_stack = np.vstack([Y_stack,Y_local])

            i += 1

        self.Y += Y_stack[1:].sum(axis = 0)

    def fuck(self):
        self.get_I()
        self.add_Noise()
        self.add_multiple_Gaussians()
    
    def unfuck(self):

        if self.name == "phi":
            X_above_Threashold = np.arange(-self.X/2,self.X/2)[self.Y_mean > self.Threashold]
        else:
            X_above_Threashold = np.arange(0,self.X)[self.Y_mean > self.Threashold]
        
        
        if len(X_above_Threashold > 2):

            self.x_retrieve_start = X_above_Threashold[0]
            self.x_retrieve_end = X_above_Threashold[-1]
            self.x_retrieved = X_above_Threashold[0] + (X_above_Threashold[-1] - X_above_Threashold[0] )/2
            self.x_retrieved_uncertainty = X_above_Threashold[-1] - X_above_Threashold[0]
        else:
            self.x_retrieved = None

    def analyse(self):

        self.reset_Y()
        self.fuck()
        #print("fucked")
        self.Y_stack = np.vstack([self.Y_stack,self.Y])
        self.Y_mean = np.mean(self.Y_stack, axis=0)
        self.unfuck()

        while len(self.Y_stack) >= self.Average_Spectra:
            self.Y_stack = np.delete(self.Y_stack,0,0)
    
    def plot(self):
        return self.fig, self.ax


    def update(self, frame):
        self.line.set_ydata(self.Y_mean)
        self.threshold_line_h.set_ydata([self.Threashold, self.Threashold])
        self.threshold_line_vl.set_xdata([self.x_retrieve_start, self.x_retrieve_start])
        self.threshold_line_vr.set_xdata([self.x_retrieve_end, self.x_retrieve_end])
        if self.x_retrieved is None:
            self.text_x_retrieved.set_text("X: failed")
        else:
            self.text_x_retrieved.set_text(f"X: {int(self.x_retrieved)} +- {int(self.x_retrieved_uncertainty)}")
        self.text_average_spectra.set_text(f"Average over: {int(self.Average_Spectra)} Spectra")
        return self.line, self.threshold_line_h, self.threshold_line_vl, self.threshold_line_vr, self.text_x_retrieved, self.text_average_spectra

def check_input():
    global running 
    
    if keyboard.is_pressed('y'):
            Signal_X.Threashold += 0.03
    
    if keyboard.is_pressed('x'):
            Signal_X.Threashold -= 0.03
    
    if keyboard.is_pressed('u'):
            Signal_X.Average_Spectra += 1
    
    if keyboard.is_pressed('l'):
            if Signal_X.Average_Spectra > 1:
                Signal_X.Average_Spectra -= 1
    
    if keyboard.is_pressed('n'):
            Signal_Y.Threashold += 0.03
    
    if keyboard.is_pressed('m'):
            Signal_Y.Threashold -= 0.03

    if keyboard.is_pressed('o'):
            Signal_Y.Average_Spectra += 1
    
    if keyboard.is_pressed('l'):
            if Signal_Y.Average_Spectra > 1:
                Signal_Y.Average_Spectra -= 1
    
    if keyboard.is_pressed('q'):
        running = False

    if running == True:
         threading.Timer(0.01, check_input).start()
 

def get_and_send_Positions():
    global running 
    game_state = get_game_state()
    X = game_state[0]["ship_x"]
    Y = game_state[0]["ship_x"]
    new_gamestate = []
    for j in game_state[1:]: # the first one is the ship position
        # x,y --> d,phi
        
        d, phi = calculate_r_phi(X,Y,j["x"],j["y"])
        Signal_X.x = d
        Signal_Y.x = phi
        print("Phi: ", phi," D: ",d)
        #print("Phi: ",int(phi))
        #print("d ",int(d))
        # Retrieve x and y:
        Signal_X.analyse()
        Signal_Y.analyse()
        if Signal_X.x_retrieved != None and Signal_Y.x_retrieved != None:
             
            x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.x_retrieved,Signal_Y.x_retrieved)
            print(j["x"], x_retrieved)
            print(j["y"], y_retrieved)
        
        
        # Rücktransformation:
        if Signal_X.x_retrieved != None and Signal_Y.x_retrieved != None:
            x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.x_retrieved,Signal_Y.x_retrieved)

            j = {"Name": "UFO","x_detected": x_retrieved ,  "y_detected": y_retrieved,"uncertaincy": np.sqrt(Signal_X.x_retrieved_uncertainty**2+Signal_Y.x_retrieved_uncertainty**2)}
            new_gamestate.append(j)
        
    update_game_state(new_gamestate)

    if running == True:
         threading.Timer(1, get_and_send_Positions).start()

     

Signal_X = Signal("distance",300,100)
Signal_Y = Signal("phi",-80,100)
running = True
# get input every n seconds
threading.Timer(0.1, get_and_send_Positions).start()
# check Input
threading.Timer(0.01, check_input).start()




ani_x = FuncAnimation(Signal_X.fig, Signal_X.update, frames=100, blit=True, interval=100)
ani_y = FuncAnimation(Signal_Y.fig, Signal_Y.update, frames=100, blit=True, interval=100)
plt.show()

    


