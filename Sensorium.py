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

# Disable all the keymaps
for key in plt.rcParams:
    if key.startswith('keymap'):
        plt.rcParams[key] = []

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

def normalize_angle(phi):
    """Normalize the angle to the range [-180, 180]."""
    phi = phi % 360
    if phi > 180:
        phi -= 360
    return phi

def C1_to_C2(phi_C1, rotation_C2):
    """
    Convert an angle from C1 to C2.
    
    Parameters:
    phi_C1 (float): Angle in C1.
    rotation_C2 (float): Rotation of C2 relative to C1 (in degrees).
    
    Returns:
    float: The angle in C2.
    """
    # Subtract the rotation of C2 from the angle in C1
    phi_C2 = phi_C1 - rotation_C2
    
    # Normalize the result to be within [-180, 180]
    return normalize_angle(phi_C2)

def C2_to_C1(phi_C2, rotation_C2):
  
    """
    Convert an angle from C2 back to C1.
    
    Parameters:
    phi_C2 (float): Angle in C2.
    rotation_C2 (float): Rotation of C2 relative to C1 (in degrees).
    
    Returns:
    float: The angle in C1.
    """
    # Add the rotation of C2 to the angle in C2
    phi_C1 = phi_C2 + rotation_C2
    
    # Normalize the result to be within [-180, 180]
    return normalize_angle(phi_C1)



class Signal:
  
    def __init__(self,test_mode):

        Range = 360 
        self.pixel_per_deg = 2

        self.X = Range*self.pixel_per_deg

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
        
        self.x_retrieve_start = 0
        self.x_retrieved = None
        self.D_retrieved = None
        self.x_retrieve_end = 0 
        self.x_retrieved_uncertainty = 0
        self.D_retrieved_uncertainty = 0
        self.Above_Threashold_Regions = []

        # Peak shaping 
        self.Noise = 0.05

        self.num_of_Gaussians = 1

        self.Sigma_aquisition_factor = 0.01
        self.Sigma = []

        self.I_aquisition_factor = 0.0065
        self.I = []
        self.I_sigma = 0.01 

        self.Sigma_local_aquisition_factor = 0.008
        self.Sigma_local =[]
        self.Sigma_local_sigma = 0.01

        
        # Plotting
        self.fig, self.ax = plt.subplots(figsize = (5,4))
        if test_mode ==True:
            self.fig_D, self.ax_D = plt.subplots(figsize = (5,4))
        
        self.horizontal_line = self.ax.axhline(self.Threashold, color='red', linestyle='--') # We only need one 
        self.vertical_lines = []
        self.vertical_lines_D = []


        self.line, = self.ax.plot(np.linspace(-180, +180,360*self.pixel_per_deg), self.Y_mean,color='black')
        if test_mode ==True:
            self.line_D, = self.ax_D.plot(np.linspace(-180, +180,360*self.pixel_per_deg), self.Y_mean,color='black')
        self.text_x_retrieved = self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, fontsize=12)
        self.text_average_spectra = self.ax.text(0.1, 0.95, "", transform=self.ax.transAxes, fontsize=12)
        if test_mode == True:
            self.text_r =                               self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, fontsize=10)
            self.text_Noise =                           self.ax.text(0.1, 0.85, "", transform=self.ax.transAxes, fontsize=10)
            self.text_I =                               self.ax.text(0.1, 0.8, "", transform=self.ax.transAxes, fontsize=10)
            self.text_Sigma =                           self.ax.text(0.1, 0.75, "", transform=self.ax.transAxes, fontsize=10)
            self.text_Sigma_aquisition_factor =         self.ax.text(0.1, 0.7, "", transform=self.ax.transAxes, fontsize=10)
            self.text_I_aquisition_factor =             self.ax.text(0.1, 0.65, "", transform=self.ax.transAxes, fontsize=10)
            self.text_I_sigma =                          self.ax.text(0.1,0.6, "", transform=self.ax.transAxes, fontsize=10)
            self.text_sigma_local_aquisition_factor =   self.ax.text(0.1, 0.55, "", transform=self.ax.transAxes, fontsize=10)
            self.text_sigma_local_sigma =               self.ax.text(0.1, 0.5, "", transform=self.ax.transAxes, fontsize=10)

        self.ax.set_ylim(-0.5, 3)
        self.ax.set_xlim(-180, 180)
        self.ax.set_xticks(np.arange(-180, 181, 60))  # Adjust the step as needed
        if test_mode ==True:
            self.ax_D.set_ylim(-0.5, 700)
        

    
    def get_I(self):
        self.I = []
        
        for r in self.r:
            if r < 700:
                I = 3-self.I_aquisition_factor*r
                if I > 0:
                    self.I.append(I)#= 2#-self.r*0.001*self.Noise+ 10*self.Noise
                else:
                    self.I.append(0)
            else:
                self.I.append(0)# = 0 
   
    def get_Sigma(self):
        self.Sigma = []
        for r in self.r:
            self.Sigma.append(self.Sigma_aquisition_factor*r*self.pixel_per_deg) 

    def get_Sigma_local(self):
        self.Sigma_local = []

        for r in self.r:
            self.Sigma_local.append(self.Sigma_local_aquisition_factor*r*self.pixel_per_deg) 

    def reset_single_spectrum(self):
        self.Y = np.zeros(self.X)
        self.D = np.zeros(self.X)

    def add_Noise(self):

        self.Y += np.random.normal(0,self.Noise,self.X)
        #self.D += np.random.normal(0,50,self.X)

    def add_Gaussian(self,X,x,I,sigma):


        Y =  I * np.exp(-((X - x) ** 2) / (2 * sigma ** 2))
        
        return Y

    def add_multiple_Gaussians(self):
        
        Y_stack = np.zeros(self.X)
        
        i = 0 
        
        while i < self.num_of_Gaussians:
            
            j = 0 
            while j < len(self.x): #für jedes phi:

                #calculate local peak parameters:
                
                I_local = np.random.normal(self.I[j], self.I[j]*self.I_sigma)# we draw from a gaussian centered at I with  a sigma of 0.5I
                x_local = np.random.normal(self.x[j]*self.pixel_per_deg, self.Sigma[j])
                sigma_local = np.random.normal(self.Sigma_local[j], self.Sigma_local[j]*self.Sigma_local_sigma)

                # Add them together in the I spectrum             
                Y_local = self.add_Gaussian(np.arange(-self.X/2, self.X/2), x_local, I_local, sigma_local)
                Y_stack = np.vstack([Y_stack,Y_local])
                
                # Change the D spectrum: 
                d_local = self.fuck_d(self.r[j])
                self.D[int(x_local- 1.5*sigma_local*self.pixel_per_deg)-180*self.pixel_per_deg:int(x_local+1.5*sigma_local*self.pixel_per_deg)-180*self.pixel_per_deg] = d_local  

                j += 1 

            i += 1 

        self.Y += Y_stack[1:].sum(axis = 0)

    def fuck_d(self,d):

        delta_d = d*0.1
        d_fucked = d + np.random.uniform(-delta_d, delta_d)

        return d_fucked
       
    def get_peak_parameters(self):
        self.get_I()
        self.get_Sigma()
        self.get_Sigma_local()

    def sort_peak_paramerters(self):

        # always display the furthest away first and overwrite if a nearer one is detected 

        sorted_indices = sorted(range(len(self.r)), key=lambda i: self.r[i], reverse=True)

        # Rearrange array1 and array2 according to the sorted order of array1
        self.x =            [self.x[i] for i in sorted_indices]
        self.r =            [self.r[i] for i in sorted_indices]
        self.I =            [self.I[i] for i in sorted_indices]
        self.Sigma =        [self.Sigma[i] for i in sorted_indices]
        self.Sigma_local =  [self.Sigma_local[i] for i in sorted_indices]
   
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

        self.reset_single_spectrum()
        self.get_peak_parameters()
        self.sort_peak_paramerters()
        
        self.add_Noise()
        self.add_multiple_Gaussians()

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
        if test_mode == True:
            self.text_r.set_text(f"R: {self.r} ")
            self.text_Noise.set_text(f"2 Noise: {np.round(self.Noise,3)} ")
            self.text_Sigma_aquisition_factor.set_text(f"3 Sigma aquisition: {np.round(self.Sigma_aquisition_factor,3)} ")
            self.text_Sigma.set_text(f"Sigma : {np.round(self.Sigma,3)} ")
            self.text_I_aquisition_factor.set_text(f"4 I aquistion: {np.round(self.I_aquisition_factor,3)} ")
            self.text_I_sigma.set_text(f"5 I sigma: {np.round(self.I_sigma,3)} ")
            self.text_I.set_text(f"I : {np.round(self.I,3)} ")
            self.text_sigma_local_aquisition_factor.set_text(f"6 Sigma local aquisition: {np.round(self.Sigma_local_aquisition_factor,3)} ")
            self.text_sigma_local_sigma.set_text(f"7 Sigma local sigma: {np.round(self.Sigma_local_sigma,3)} ")
            
            # Combine single artist with the list of lines 
            return [self.line, self.horizontal_line, self.text_average_spectra, self.text_r, self.text_Noise, self.text_Sigma_aquisition_factor, self.text_I_aquisition_factor, 
                    self.text_I_sigma,  self.text_sigma_local_aquisition_factor, self.text_sigma_local_sigma, self.text_Sigma, self.text_I] + self.vertical_lines
        else:
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

mode = 0 
def check_input():
    global running 
    global mode
    global test_mode 

    if test_mode == True: 
        if keyboard.is_pressed('1'):
            mode = 1
        if keyboard.is_pressed('2'):
            mode = 2
        if keyboard.is_pressed('3'):
            mode = 3
        if keyboard.is_pressed('4'):
            mode = 4
        if keyboard.is_pressed('5'):
            mode = 5
        if keyboard.is_pressed('6'):
            mode = 6
        if keyboard.is_pressed('7'):
            mode = 7

        if keyboard.is_pressed('a'):
            if mode == 1:
                Signal_X.r[0] +=1

            if mode == 2:
                if Signal_X.Noise < 1:
                    Signal_X.Noise +=0.001

            if mode == 3:
                Signal_X.Sigma_aquisition_factor += 0.001

            if mode == 4:
                Signal_X.I_aquisition_factor +=0.001

            if mode == 5:
                Signal_X.I_sigma +=0.1

            if mode == 6:
                Signal_X.Sigma_local_aquisition_factor +=0.001

            if mode == 7:
                Signal_X.Sigma_local_sigma +=0.001


        if keyboard.is_pressed('d'):
            if mode == 1:
                Signal_X.r[0] -=1

            if mode == 2:
                if Signal_X.Noise > 0.01:
                    Signal_X.Noise -=0.001

            if mode == 3:
                if Signal_X.Sigma_aquisition_factor > 0.001:
                    Signal_X.Sigma_aquisition_factor -= 0.001

            if mode == 4:
                if Signal_X.I_aquisition_factor > 0.0001:
                    Signal_X.I_aquisition_factor -=0.0001

            if mode == 5:
                if Signal_X.I_sigma > 0.01:
                    Signal_X.I_sigma -=0.01

            if mode == 6:
                if Signal_X.Sigma_local_aquisition_factor > 0.001:
                    Signal_X.Sigma_local_aquisition_factor -=0.001

            if mode == 7:
                if Signal_X.Sigma_local_sigma > 0.001:
                    Signal_X.Sigma_local_sigma -=0.001

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
    Phi = game_state[0]["ship_phi"]
    response = {"x": [], "y": [], "uncertainty": []}
    Signal_X.x = []
    Signal_X.r = []
    x = 0
    y = 0 

    for j in game_state[1:]: # the first one is the ship position
        # x,y --> d,phi
        
        d, phi = calculate_r_phi(X,Y,j["x"],j["y"])
        phi = C1_to_C2(phi,Phi)
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
            phi_retrieved = C2_to_C1(Signal_X.x_retrieved[i],Phi)
            x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.D_retrieved[i],phi_retrieved)
            response["x"].append(int(x_retrieved))
            response["y"].append(int(y_retrieved))
            response["uncertainty"].append(int(Signal_X.x_retrieved_uncertainty[i]+7))

        print("x retrieved", x_retrieved)
        print("y retrieved", y_retrieved)
        update_game_state(response)    
        print("response sent")
    
    if running == True:
         threading.Timer(1, get_and_send_Positions).start()

def test_initialize():
    global running 


    ### Simulate the gamestate ###

    # first we add the ship position
    data = []
    data.append({"ship_x": 0,"ship_y": 0})
    
    # then we add an enemy ship
    x = 0
    y = -100
    extracted = {"Name": "enemy1", "x": x, "y": y}
    data.append(extracted)


    # then we pack it in the form the gamestate will have     
    response = json.dumps(data).encode('utf-8')
    game_state = json.loads(response.decode('utf-8'))

    response = {"x": [], "y": [], "uncertainty": []}
    # start to readout the gamestate 
    X = game_state[0]["ship_x"]
    Y = game_state[0]["ship_y"]
    
    Signal_X.x = []
    Signal_X.r = []


    for j in game_state[1:]: # the first one is the ship position
        # x,y --> d,phi
        
        d, phi = calculate_r_phi(X,Y,j["x"],j["y"])
        Signal_X.x.append(phi)
        Signal_X.r.append(d)
        #print("Input:"," Phi: ", phi, " D: ",d)
    
def test():

    Signal_X.analyse()

    
    #print("Output:"," Phi: ", Signal_X.x_retrieved, " D: ",Signal_X.D_retrieved)


    # Output the retrieved data

    #print("d",Signal_X.r, Signal_X.D_retrieved)
    #print("phi",Signal_X.x, Signal_X.x_retrieved)
    X = 0 
    Y = 0 
    phi = Signal_X.x
    r = Signal_X.r
    x,y = pol2cart(X,Y,r[0],phi[0])

    for i in range(len(Signal_X.x_retrieved)):
        #print(X,Y,Signal_X.x_retrieved[i],Signal_X.D_retrieved[i])
        x_retrieved, y_retrieved = pol2cart(X,Y,Signal_X.D_retrieved[i],Signal_X.x_retrieved[i])
        #response["x"].append(int(x_retrieved))
        #response["y"].append(int(y_retrieved))
        #response["uncertainty"].append(int(Signal_X.x_retrieved_uncertainty[i]))

        print("dx: ", x- x_retrieved,"dy: ", y-y_retrieved)
        #print(x2- x_retrieved, y2-y_retrieved)

    #update_game_state(response)    
    
    if running == True:
         threading.Timer(0.3, test).start()


running = True
test_mode = True
Signal_X = Signal(test_mode)

if test_mode == True:
    test_initialize()
    threading.Timer(0.1, test).start()
else:
    threading.Timer(0.1, get_and_send_Positions).start()


# check Input
threading.Timer(0.01, check_input).start()

ani_phi = FuncAnimation(Signal_X.fig, Signal_X.update, frames=100, blit=True, interval=100)
if test_mode ==True:
    ani_D = FuncAnimation(Signal_X.fig_D, Signal_X.update_D, frames=100, blit=True, interval=100)
plt.show()

    


