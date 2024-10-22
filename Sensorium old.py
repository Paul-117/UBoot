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
        print("connected")
        s.connect((HOST, PORT))
        command = json.dumps({"type": "get","ID": "Sensorium"}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        #print(data)
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
  
    def __init__(self,Manager, test_mode):

        Range = 360 
        self.pixel_per_deg = 1

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
        self.Manager = Manager
        # Peak shaping 
        self.Noise = 0.05

        self.num_of_Gaussians = 1

        self.Sigma_aquisition_factor = 0.01
        self.Sigma = []

        self.I_aquisition_factor = 0.01
        self.I = []
        self.I_sigma = 0.01 

        self.Sigma_local_aquisition_factor = 0.008
        self.Sigma_local =[]
        self.Sigma_local_sigma = 0.01

        
        # Plotting
        self.fig, self.ax = plt.subplots(figsize = (5,4))
        self.ax.set_facecolor('black')
        self.ax.grid(True, which='both', color='green', linestyle=':', linewidth=0.5)

        if test_mode ==True:
            self.fig_D, self.ax_D = plt.subplots(figsize = (5,4))
        
        self.horizontal_line = self.ax.axhline(self.Threashold, color='red', linestyle='dashed',linewidth=1) # We only need one 
        self.vertical_lines = []
        self.vertical_lines_D = []


        self.line, = self.ax.plot(np.linspace(-180, +180,360*self.pixel_per_deg), self.Y_mean, color='lime', linestyle='dotted', linewidth=1)
        if test_mode ==True:
            self.line_D, = self.ax_D.plot(np.linspace(-180, +180,360*self.pixel_per_deg), self.Y_mean,color='black')
        self.text_x_retrieved = self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, fontsize=12)
        self.text_average_spectra = self.ax.text(0.1, 0.95, "", transform=self.ax.transAxes, fontsize=12)
        if test_mode == True:
            c = "lime"
            self.text_r =                               self.ax.text(0.1, 0.9, "", transform=self.ax.transAxes, color = c, fontsize=10)
            self.text_Noise =                           self.ax.text(0.1, 0.85, "", transform=self.ax.transAxes,color = c, fontsize=10)
            self.text_I =                               self.ax.text(0.1, 0.8, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_Sigma =                           self.ax.text(0.1, 0.75, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_Sigma_aquisition_factor =         self.ax.text(0.1, 0.7, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_I_aquisition_factor =             self.ax.text(0.1, 0.65, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_I_sigma =                          self.ax.text(0.1,0.6, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_sigma_local_aquisition_factor =   self.ax.text(0.1, 0.55, "", transform=self.ax.transAxes, color = c,fontsize=10)
            self.text_sigma_local_sigma =               self.ax.text(0.1, 0.5, "", transform=self.ax.transAxes, color = c,fontsize=10)

        self.ax.set_ylim(-0.5, 3)
        self.ax.set_xlim(-180, 180)
        self.ax.set_xticks(np.arange(-180, 181, 60))  # Adjust the step as needed
        if test_mode ==True:
            self.ax_D.set_ylim(-0.5, 700)
        
    def get_I(self):
        self.I = []
        
        for r in self.r:
            I = np.maximum(4.5 + self.Manager.get_actual_power()["Peak Intensity"] - self.I_aquisition_factor*r, 0)
            self.I.append(I)

    def get_Sigma(self):
        self.Sigma = []
        
        for r in self.r:
            S = 00.03*r / self.Manager.get_actual_power()["Peak Position Stability"]
            self.Sigma.append(S) 

    def get_Sigma_local(self):
        self.Sigma_local = []
        for r in self.r:
            W = np.maximum(-2 + (0.01*r)/ self.Manager.get_actual_power()["Local Peak Width"], 0.1)
            self.Sigma_local.append(W*self.pixel_per_deg) 

    def reset_single_spectrum(self):
        self.Y = np.zeros(self.X)
        self.D = np.zeros(self.X)

    def add_Noise(self):
        
        N = np.maximum(0.1- self.Manager.get_actual_power()["Noise level"]*0.01,0.01)
        self.Noise = N
        self.Y += np.random.normal(0,N,self.X)
        #self.D += np.random.normal(0,50,self.X)

    def add_Gaussian(self,X,x,I,sigma):


        Y =  I * np.exp(-((X - x) ** 2)* 2 / (sigma ** 2))
        
        return Y

    def add_multiple_Gaussians(self):
        
        Y_stack = np.zeros(self.X)
        
        i = 0 
        
        while i < self.num_of_Gaussians:
            
            j = 0 
            while j < len(self.x): #für jedes phi:

                #calculate local peak parameters:
                

                I_local = np.random.normal(self.I[j], self.I[j]*self.I_sigma)# we draw from a gaussian centered at I with  a sigma of 0.5I
                x_local = np.random.normal(self.x[j]*self.pixel_per_deg, self.Sigma[j]/2)
                
                sigma_local = np.random.normal(self.Sigma_local[j], self.Sigma_local_sigma)

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
        
        jump_indices = np.where(np.diff(X_above_Threashold) > 3*self.pixel_per_deg )[0]
        # Split the array at the jumps
        self.Above_Threashold_Regions = np.split(X_above_Threashold, jump_indices + 1)
                         
        for region in self.Above_Threashold_Regions:
            if len(region) > 1:
                a = (-180 + int(region[0]) )*self.pixel_per_deg # region sind die x werte diese gehen von -180 bis 180 wir wollen aber die array indices 
                b = (-180 + int(region[-1]) )*self.pixel_per_deg
                
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
        line = self.ax.axvline(x_position, color='red', linestyle='dashed', linewidth=1)
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
        if len(self.Above_Threashold_Regions) > 1:
            for i in range(len(self.Above_Threashold_Regions)):
                if len(self.Above_Threashold_Regions[i]) > 0:
                    self.add_vertical_line_D(self.Above_Threashold_Regions[i][0])
                    self.add_vertical_line_D(self.Above_Threashold_Regions[i][-1])


        return [self.line_D] + self.vertical_lines_D

class PowerDistributionManager:
    def __init__(self, input_power=4):
        self.input_power = input_power  # Total input power in MW

        # Subsystems and their initial percentages (representing resistances)
        self.subsystems = {
            'Noise level': 0.25,           # 25%
            'Peak Intensity': 0.25,        # 25%
            'Peak Position Stability': 0.25, # 25%
            'Local Peak Width': 0.25        # 25%
        }

        self.subsystem_names = list(self.subsystems.keys())
        self.selected_subsystem_idx = 0  # Start with the first subsystem selected
        self.step_size = 0.01  # Step size for percentage adjustment

        # Set up the plot for displaying power distribution
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.fig.patch.set_facecolor('black')
        
        # Set up animation but do not start yet
        self.ani = None
        self.texts = []  # List to hold text objects for blitting

        # Register key event listeners for Tab, Up, and Down keys
        keyboard.on_press_key('tab', self.on_tab_event)
        keyboard.on_press_key('up', self.on_up_event)
        keyboard.on_press_key('down', self.on_down_event)

    def on_tab_event(self, event):
        """Move to the next subsystem."""
        self.selected_subsystem_idx = (self.selected_subsystem_idx + 1) % len(self.subsystem_names)

    def on_up_event(self, event):
        """Increase the percentage of the selected subsystem."""
        selected_subsystem = self.subsystem_names[self.selected_subsystem_idx]
        self.subsystems[selected_subsystem] += self.step_size
        if self.subsystems[selected_subsystem] > 1:
            self.subsystems[selected_subsystem] = 1  # Cap at 100%

    def on_down_event(self, event):
        """Decrease the percentage of the selected subsystem."""
        selected_subsystem = self.subsystem_names[self.selected_subsystem_idx]
        self.subsystems[selected_subsystem] -= self.step_size
        if self.subsystems[selected_subsystem] < 0:
            self.subsystems[selected_subsystem] = 0  # Ensure no negative values

    def calculate_power_distribution(self):
        """
        Calculate power distribution based on resistance.
        - Subsystem percentages represent resistances.
        - Higher percentages get higher power.
        - Subsystems with 0% receive no power.
        """
        total_resistance = sum(self.subsystems.values())
        actual_power = {}

        for subsystem, percentage in self.subsystems.items():
            if percentage == 0:
                actual_power[subsystem] = 0
            else:
                actual_power[subsystem] = (percentage / total_resistance) * self.input_power

        return actual_power

    def get_actual_power(self):
        """
        Maintain compatibility with previous use cases.
        Return the power distributed to each subsystem.
        """
        return self.calculate_power_distribution()  # Use the updated logic to calculate actual power

    def format_display_line(self, subsystem, percentage, power, selected=False):
        """Format the display line for the plot."""
        symbol = "> " if selected else "  "  # Use ">" for selected, " " otherwise
        formatted_line = f"{symbol}{subsystem:<25}{percentage * 100:>6.1f}%   {power:>6.2f} MW"
        return formatted_line

    def update_display(self, frame):
        """Update the display on the plot for each frame of the animation."""
        actual_power = self.get_actual_power()

        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, len(self.subsystems) + 1)
        self.ax.set_facecolor('black')  # Set the background color to black for the axis
        self.ax.axis('off')

        self.texts = []  # Reset the texts list for each frame

        # Display each subsystem with aligned columns for subsystem name, percentage, and power
        for i, (subsystem, power) in enumerate(actual_power.items()):
            percentage = self.subsystems[subsystem]
            selected = i == self.selected_subsystem_idx
            display_line = self.format_display_line(subsystem, percentage, power, selected)
            # Create a new text object for each subsystem
            text = self.ax.text(0.05, len(self.subsystems) - i, display_line, fontsize=12, family="monospace", color='lime')
            self.texts.append(text)  # Store the text object for blitting

        self.ax.set_title(f'Power Distribution of {self.input_power} MW', fontsize=14, color='lime')

        return self.texts  # Return the list of text objects for blitting

class SignalIntensityPlotter:
    
    def __init__(self,manager):
        self.Manager = manager
        # Initial parameters for all functions
        self.f1 = 1       # Initial value for f
        self.k1 = 0.01    # Initial value for k
        self.f2 = 1      # Initial value for f2
        self.k2 = 0.01     # Initial value for k2
        self.f3 = 1      # Initial value for f3
        self.k3 = 1      # Initial value for k3
        self.f4 = 1      # Initial value for f4
        self.k4 = 1      # Initial value for k4
        
        # Distance range from 0 to 500
        self.r = np.linspace(0, 500, 100)  
        
        # Calculate initial values for all functions
        self.I = self.calculate_intensity()  
        self.S = self.calculate_sigma()      
        self.N = self.calculate_noise()       # Renamed from calculate_new_function to calculate_noise
        self.W = self.calculate_width()       # Renamed from calculate_L_function to calculate_width

        # Set up the plot with five subplots
        self.fig, (self.ax1, self.ax2, self.ax3, self.ax4,) = plt.subplots(4, 1, figsize=(8, 15))  # 5 rows, 1 column
        
        # First subplot for intensity I
        self.line_I, = self.ax1.plot(self.r, self.I, color='cyan', label='Intensity I')
        self.ax1.set_title(f'Signal Intensity: I = 3 + {self.f1} - {self.k1} * r', color='lime')
        self.ax1.set_xlabel('Distance r', color='lime')
        self.ax1.set_ylabel('Intensity I', color='lime')
        self.ax1.tick_params(axis='both', colors='lime')
        self.ax1.set_facecolor('black')

        # Second subplot for signal S
        self.line_S, = self.ax2.plot(self.r, self.S, color='magenta', label='Sigma S')
        self.ax2.set_title(f'Sigma: S = (12.5*2**(self.r/100)) / {self.f2}', color='lime')
        self.ax2.set_xlabel('Distance r', color='lime')
        self.ax2.set_ylabel('Sigma S', color='lime')
        self.ax2.tick_params(axis='both', colors='lime')

        # Third subplot for noise N
        self.line_N, = self.ax3.plot(self.r, self.N, color='yellow', label='Noise N')
        self.ax3.set_title(f'Noise: N = {0.1- self.f3*0.02}', color='lime')
        self.ax3.set_xlabel('Distance r', color='lime')
        self.ax3.set_ylabel('Noise N', color='lime')
        self.ax3.set_ylim(0,0.1)
        self.ax3.tick_params(axis='both', colors='lime')

        # Fifth subplot for width W
        self.line_W, = self.ax4.plot(self.r, self.W, color='red', label='Width W')
        self.ax4.set_title('Width: W = f4 * k4 * r', color='lime')
        self.ax4.set_xlabel('Distance r', color='lime')
        self.ax4.set_ylabel('Width W', color='lime')
        self.ax4.tick_params(axis='both', colors='lime')
        
        # Set the background color for the entire figure
        self.fig.patch.set_facecolor('black')
        self.ax1.set_facecolor('black')
        self.ax2.set_facecolor('black')
        self.ax3.set_facecolor('black')
        self.ax4.set_facecolor('black')

        
        # Adjust spacing between subplots
        plt.subplots_adjust(hspace=1)  # Increase vertical space between plots
    
    def update_factors(self):
        
        self.f1 = self.Manager.get_actual_power()["Peak Intensity"]
        self.f2 = self.Manager.get_actual_power()["Peak Position Stability"]
        self.f3 = self.Manager.get_actual_power()["Noise level"]
        self.f4 = self.Manager.get_actual_power()["Local Peak Width"]

    def calculate_intensity(self):
        """Calculate intensity I based on the current f, k, and r."""
        r = self.r
        
        I = np.maximum(3 + self.Manager.get_actual_power()["Peak Intensity"] - (0.01*r), 0)
        return I * np.ones_like(self.r)

    def calculate_sigma(self):
        """Calculate signal S based on the current f2 and k2."""
        r = self.r
        S = 00.05*r / self.Manager.get_actual_power()["Peak Position Stability"]
        return S * np.ones_like(self.r)  # S is constant for now

    def calculate_noise(self):
        """Calculate N based on the current f3, k3, and r."""
        
        N = 0.1- self.Manager.get_actual_power()["Noise level"]*0.02
        return N* np.ones_like(self.r)    # N is a linear function of r

    def calculate_width(self):
        """Calculate width based on the current f4, k4, and r."""
        r = self.r
        W = (1.5*2**(r/100)) / self.Manager.get_actual_power()["Local Peak Width"]
        
        return W* np.ones_like(self.r)  # Width is a linear function of r

    def update_plot(self, frame):
        """Update the plots with new intensity, signal, and new function values."""
        self.I = self.calculate_intensity()
        self.S = self.calculate_sigma()
        self.N = self.calculate_noise()
        self.W = self.calculate_width()
        
        # Update the lines
        self.line_I.set_ydata(self.I)
        self.line_S.set_ydata(self.S)
        self.line_N.set_ydata(self.N)
        self.line_W.set_ydata(self.W)
        
        # Update titles
        self.ax1.set_title(f'Signal Intensity: I = 3 + {self.f1} - {self.k1} * r', color='lime')
        self.ax2.set_title('Signal: S = f2 * k2', color='lime')
        self.ax3.set_title('Noise: N = f3 * k3 * r', color='lime')
        self.ax4.set_title('Width: W = f4 * k4 * r', color='lime')
        return self.line_I, self.line_S, self.line_N, self.line_W

    def run(self):
        """Run the plot display."""
        plt.show()  # Show the plot

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
        
    if keyboard.is_pressed('p'):
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
    y = -500
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

        #print("dx: ", x- x_retrieved,"dy: ", y-y_retrieved)
        #print(x2- x_retrieved, y2-y_retrieved)

    #update_game_state(response)    
    
    if running == True:
         threading.Timer(0.3, test).start()


running = True
test_mode = True



manager = PowerDistributionManager(24)

Signal_X = Signal(manager,test_mode)

#plotter = SignalIntensityPlotter(manager)
    
if test_mode == True:
    test_initialize()
    threading.Timer(0.1, test).start()
else:
    threading.Timer(1, get_and_send_Positions).start()


# check Input
threading.Timer(0.01, check_input).start()


ani = FuncAnimation(manager.fig, manager.update_display, frames=100, blit=True, interval=100)
#ani2 = FuncAnimation(plotter.fig, plotter.update_plot, frames=100, interval=100, blit=True)
ani_phi = FuncAnimation(Signal_X.fig, Signal_X.update, frames=100, blit=True, interval=100)
if test_mode ==True:
    #ani_D = FuncAnimation(Signal_X.fig_D, Signal_X.update_D, frames=100, blit=True, interval=100)
    pass
plt.show()

    


