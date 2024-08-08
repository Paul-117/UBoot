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

        #s.close()
        
def retrieve_xy(x_ship,X,y_ship,Y):
    # Achtung funktion ist auf 1000m Reichweite ausgelegt 
    
    x_relative = X-x_ship
    y_relative = Y-y_ship
    r = np.sqrt(x_relative**2+y_relative**2)
    sigma = 0.05*r
    x = np.random.normal(loc=X, scale=sigma, size=None)
    y = np.random.normal(loc=Y, scale=sigma, size=None)
    
    return x,y,sigma*2

#r = np.sqrt(coordinates[0]**2+coordinates[1]**2)

def calculate_r_phi(X,Y,x,y):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)+90+360)%360

    if angle > 180:
        angle = -(360-angle)
    
    return distance, angle 

def pol2cart(X, Y, d, phi):
    
    x = X + d * np.sin(math.radians(phi))
    y = Y - d * np.cos(math.radians(phi))
    return (round(x), round(y))

class Signal:
  
    def __init__(self):


        self.X = 360
        
        self.Y = np.zeros(self.X)
        self.Y_stack = np.zeros(self.X)
        self.Y_mean = np.zeros(self.X)
        self.D = np.zeros(self.X)
        self.D_stack = np.zeros(self.X)
        self.D_mean = np.zeros(self.X)
        self.x = []
        self.r = []
        self.Threashold = 1
        self.Average_Spectra = 1
        self.Noise = 0.1
        self.num_of_Gaussians = 1
        self.I = []
        self.Sigma = []
        self.x_retrieve_start = 0
        self.x_retrieved = None
        self.D_retrieved = None
        self.x_retrieve_end = 0 
        self.x_retrieved_uncertainty = 0
        self.D_retrieved_uncertainty = 0
        self.Above_Threashold_Regions = []

        
        
        # Plotting
        self.fig, self.ax = plt.subplots(figsize = (5,4))
        self.fig_D, self.ax_D = plt.subplots(figsize = (5,4))
        
        self.horizontal_line = self.ax.axhline(self.Threashold, color='red', linestyle='--') # We only need one 
        self.vertical_lines = []
        self.vertical_lines_D = []


        self.line, = self.ax.plot(np.arange(-self.X/2, +self.X/2), self.Y_mean,color='black')
        self.line_D, = self.ax_D.plot(np.arange(-self.X/2, +self.X/2), self.Y_mean,color='black')
        self.text_x_retrieved = self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, fontsize=12)
        self.text_average_spectra = self.ax.text(0.1, 0.85, "", transform=self.ax.transAxes, fontsize=12)
        self.ax.set_ylim(-0.5, 3)
        self.ax_D.set_ylim(-0.5, 700)
        
        # Calculations
        self.get_I()
        self.get_Sigma()
        #print(self.I,self.Sigma)
    
    def moving_average(self,array, window_size):
        return np.convolve(array, np.ones(window_size)/window_size, mode='same')


    def get_I(self):
        self.I = []
        
        for r in self.r:
            if r < 700:
                self.I.append(7)#= 2#-self.r*0.001*self.Noise+ 10*self.Noise
                
            else:
                self.I.append(0)# = 0 
    
    def get_Sigma(self):
        self.Sigma = []
        for r in self.r:

            self.Sigma.append(0.1*r) 

    def reset_Y(self):
        self.Y = np.zeros(self.X)
        self.D = np.zeros(self.X)

    def add_Noise(self):

        self.Y += np.random.normal(0,self.Noise,self.X)
        self.D += np.random.normal(0,50,self.X)

    def add_Gaussian(self,X,x,I,sigma):

        Y = I*stats.norm.pdf(X, x, sigma)

        return Y

    def add_multiple_Gaussians(self):
        Y_stack = np.zeros(self.X)
        i = 0 
        
        while i < self.num_of_Gaussians:
            
            j = 0 
            while j < len(self.x):
                    
                I_local = np.random.uniform(0.7, 1) * self.I[j]
                sigma_local = np.random.uniform(0.1 * self.Sigma[j], 0.2 * self.Sigma[j])
                x_local = np.random.normal(self.x[j], self.Sigma[j]/5)
            
                Y_local = self.add_Gaussian(np.arange(-self.X/2, self.X/2), x_local, I_local, sigma_local)
                
                Y_stack = np.vstack([Y_stack,Y_local])
                
                j += 1 

            i += 1 

        self.Y += Y_stack[1:].sum(axis = 0)

    def fuck_d(self,d):

        delta_d = d*0.1
        d_fucked = d + np.random.uniform(-delta_d, delta_d)

        return d_fucked
    
    def fuck_D(self):

        # always display the furthest away first and overwrite if a nearer one is detected 

        sorted_indices = sorted(range(len(self.r)), key=lambda i: self.r[i], reverse=True)

        # Rearrange array1 and array2 according to the sorted order of array1
        sorted_r = [self.r[i] for i in sorted_indices]
        sorted_sigma = [self.Sigma[i] for i in sorted_indices]


        for i,sigma in enumerate(self.Sigma):
            #d_local = self.fuck_d(self.r[i])
            d_local = self.r[i]
            self.D[int(self.x[i]-sigma/2 * 1.5)-180:int(self.x[i]+sigma/2 * 1.5)-180] = d_local

    def fuck(self):
        self.get_I()
        self.get_Sigma()
        #self.add_Noise()
        self.fuck_D()
        self.add_multiple_Gaussians()
    
    def unfuck(self):

        self.x_retrieved = []
        self.x_retrieved_uncertainty = []
        self.D_retrieved = []
        self.D_retrieved_uncertainty = []
        self.Above_Threashold_Regions = []
        


        X_above_Threashold = np.arange(-self.X/2,self.X/2)[self.Y_mean > self.Threashold]
        
        jump_indices = np.where(np.diff(X_above_Threashold) > 10 )[0]
        # Split the array at the jumps
        self.Above_Threashold_Regions = np.split(X_above_Threashold, jump_indices + 1)
                         
        for region in self.Above_Threashold_Regions:
            if len(region) > 1:
                a = -180 + int(region[0]) # region sind die x werte diese gehen von -180 bis 180 wir wollen aber die array indices 
                b = -180 + int(region[-1])

                self.x_retrieved.append(int(region[0] + (region[-1] - region[0] )/2 ))
                self.x_retrieved_uncertainty.append(int(region[-1] - region[0] ))
                #self.D_retrieved.append(int(np.mean(self.D_mean[a:b])))
                self.D_retrieved.append(int(np.max(self.D_mean[a:b])))
                self.D_retrieved_uncertainty.append(np.max(self.D_mean[a:b]) - np.min(self.D_mean[a:b])) 
  
    def analyse(self):

        self.reset_Y()
        self.fuck()
       
        self.Y_stack = np.vstack([self.Y_stack,self.Y])
        self.Y_mean = np.mean(self.Y_stack, axis=0)

        self.D_stack = np.vstack([self.D_stack,self.D])
        self.D_mean = np.mean(self.D_stack, axis=0)

        # self.Y_mean normieren nicht nur mit einem max value sondern mit den obersten 50 

        y = np.sort(self.Y_mean) # sort array
        y = y[::-1] # reverse sort order
        y = y[0:1] # take a slice of the first 5

        max_Y = np.mean(y)
        factor = 1/max_Y
        print(factor)
        #Y_averaged = self.moving_average(self.Y_mean,3)
        #self.D_mean = self.D_mean*self.Y_mean*factor
        
        self.unfuck()

        while len(self.Y_stack) >= self.Average_Spectra:
            self.D_stack = np.delete(self.D_stack,0,0)
            self.Y_stack = np.delete(self.Y_stack,0,0)

    def plot(self):
        return self.fig, self.ax

    def add_vertical_line(self, x_position):
        line = self.ax.axvline(x_position, color='red', linestyle='-')
        self.vertical_lines.append(line)

    def add_vertical_line_D(self, x_position):
        line_D = self.ax_D.axvline(x_position, color='red', linestyle='-')
        self.vertical_lines_D.append(line_D)
    
    def update(self, frame):

        # Emty list 
        for line in self.vertical_lines:
            line.remove()
        self.vertical_lines = []

        # Display the current Threashold
        self.horizontal_line.set_ydata([self.Threashold, self.Threashold])

        # Man könnte das in die Evaluation legen 
        
             
        for i in range(len(self.Above_Threashold_Regions)):
            if len(self.Above_Threashold_Regions[i]) > 0:
                self.add_vertical_line(self.Above_Threashold_Regions[i][0])
                self.add_vertical_line(self.Above_Threashold_Regions[i][-1])

        # Signal updaten 
        self.line.set_ydata(self.Y_mean)
        # Signal D updaten 
        

        '''
        string = ""
        for i in self.x_retrieved:
             string += ""
        if self.x_retrieved is None:
            self.text_x_retrieved.set_text("X: failed")
        else:
            self.text_x_retrieved.set_text(f"X: {int(self.x_retrieved)} +- {int(self.x_retrieved_uncertainty)}")
        '''

        self.text_average_spectra.set_text(f"Average over: {int(self.Average_Spectra)} Spectra")

        # Combine single artist with the list of lines 
        return [self.line, self.horizontal_line, self.text_average_spectra] + self.vertical_lines
    
    def update_D(self, frame):
        
        self.line_D.set_ydata(self.D_mean)

        # Emty list 
        for line in self.vertical_lines_D:
            line.remove()
        self.vertical_lines_D = []

        for i in range(len(self.Above_Threashold_Regions)):
            if len(self.Above_Threashold_Regions[i]) > 0:
                self.add_vertical_line_D(self.Above_Threashold_Regions[i][0])
                self.add_vertical_line_D(self.Above_Threashold_Regions[i][-1])


        return [self.line_D] + self.vertical_lines_D

def check_input():
    global running 
    
    if keyboard.is_pressed('y'):
            Signal_X.Threashold += 0.01
            #Signal_Y.Threashold += 0.01
    
    if keyboard.is_pressed('x'):
            Signal_X.Threashold -= 0.01
            #Signal_Y.Threashold -= 0.01
    
    if keyboard.is_pressed('c'):
            Signal_X.Average_Spectra += 1
            #Signal_Y.Average_Spectra += 1
    if keyboard.is_pressed('v'):
            
            if Signal_X.Average_Spectra > 1:
                Signal_X.Average_Spectra -= 1
            #if Signal_Y.Average_Spectra > 1:
            #    Signal_Y.Average_Spectra -= 1
        
    if keyboard.is_pressed('q'):
        running = False

    if running == True:
         threading.Timer(0.01, check_input).start()
 
def get_and_send_Positions():
    global running 
    game_state = get_game_state()
    response = {"x": [], "y": [], "uncertainty": []}
    X = game_state[0]["ship_x"]
    Y = game_state[0]["ship_y"]
    response = {"x": [], "y": [], "uncertainty": []}
    Signal_X.x = []
    Signal_X.r = []
    x = 0
    y = 0 

    for j in game_state[1:]: # the first one is the ship position
        # x,y --> d,phi
        
        d, phi = calculate_r_phi(X,Y,j["x"],j["y"])
        print("x",j["x"])
        print("y",j["y"])
        print("d",d)
        print("phi",phi)
        Signal_X.x.append(phi)
        Signal_X.r.append(d)
        #print("Input:"," Phi: ", phi, " D: ",d)

        
    Signal_X.analyse()

    
    #print("Output:"," Phi: ", Signal_X.x_retrieved, " D: ",Signal_X.D_retrieved)


    # Output the retrieved data
    if len(Signal_X.x_retrieved) != 0:
        for i in range(len(Signal_X.x_retrieved)):
            print("d retrieved", Signal_X.D_retrieved[i])
            print("phi retrieved", Signal_X.x_retrieved[i])
            x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.D_retrieved[i],Signal_X.x_retrieved[i])
            response["x"].append(int(x_retrieved))
            response["y"].append(int(y_retrieved))
            response["uncertainty"].append(int(Signal_X.x_retrieved_uncertainty[i]))

        print("x retrieved", x_retrieved)
        print("y retrieved", y_retrieved)
        update_game_state(response)    
        print("response sent")
    
    if running == True:
         threading.Timer(1, get_and_send_Positions).start()

##### Test ####

#extracted = {"Name": "enemy1", "x": -100, "y": 300}
#data.append(extracted)




def test():
    global running 

    data = []
    data.append({"ship_x": 0,"ship_y": 0})
    x = 100#np.random.uniform(-353, 353)
    y = 100#np.random.uniform(-353, 353)

    #print("x", x, "y", y)
    extracted = {"Name": "enemy2", "x": x, "y": y}
    data.append(extracted)
    
    x2 = 300#np.random.uniform(-353, 353)
    y2 = -300#np.random.uniform(-353, 353)
    extracted = {"Name": "enemy2", "x": x2, "y": y2}
    data.append(extracted)
    
    response = json.dumps(data).encode('utf-8')
    game_state = json.loads(response.decode('utf-8'))

    X = game_state[0]["ship_x"]
    Y = game_state[0]["ship_y"]
    response = {"x": [], "y": [], "uncertainty": []}
    Signal_X.x = []
    Signal_X.r = []


    for j in game_state[1:]: # the first one is the ship position
        # x,y --> d,phi
        
        d, phi = calculate_r_phi(X,Y,j["x"],j["y"])
        Signal_X.x.append(phi)
        Signal_X.r.append(d)
        #print("Input:"," Phi: ", phi, " D: ",d)

        
    Signal_X.analyse()

    
    #print("Output:"," Phi: ", Signal_X.x_retrieved, " D: ",Signal_X.D_retrieved)


    # Output the retrieved data

    print("d",Signal_X.r, Signal_X.D_retrieved)
    print("phi",Signal_X.x, Signal_X.x_retrieved)
    for i in range(len(Signal_X.x_retrieved)):
        #print(X,Y,Signal_X.x_retrieved[i],Signal_X.D_retrieved[i])
        x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.D_retrieved[i],Signal_X.x_retrieved[i])
        response["x"].append(int(x_retrieved))
        response["y"].append(int(y_retrieved))
        response["uncertainty"].append(int(Signal_X.x_retrieved_uncertainty[i]))

        #print(x- x_retrieved, y-y_retrieved)
        #print(x2- x_retrieved, y2-y_retrieved)

    #update_game_state(response)    
    
    if running == True:
         threading.Timer(1, test).start()

Signal_X = Signal()

running = True
# get input every n seconds
threading.Timer(0.1, get_and_send_Positions).start()
#threading.Timer(0.1, test).start()
# check Input
threading.Timer(0.01, check_input).start()

ani_phi = FuncAnimation(Signal_X.fig, Signal_X.update, frames=100, blit=True, interval=100)
ani_D = FuncAnimation(Signal_X.fig_D, Signal_X.update_D, frames=100, blit=True, interval=100)
plt.show()

    


