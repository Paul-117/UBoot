import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import keyboard  # using module keyboard


from scipy.optimize import curve_fit 
import matplotlib.pyplot as mpl 

#r = np.sqrt(coordinates[0]**2+coordinates[1]**2)

class Signal:
  
    def __init__(self,x,r):

        self.X = 1000
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
        self.Threashold = 1
        self.x_retrieve_start = 0
        self.x_retrieve_end = 0 
        self.x_retrieved_uncertainty = 0
        self.get_I()
        self.get_Sigma()
        print(self.I,self.Sigma)
    
        
        

    def get_I(self):

        if self.r < 500:
            self.I = -self.r*0.001*self.Noise+ 10*self.Noise
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
            
            Y_local = self.add_Gaussian(np.arange(self.X),x_local,I_local,sigma_local)
            Y_stack = np.vstack([Y_stack,Y_local])

            i += 1

        self.Y += Y_stack[1:].sum(axis = 0)

    def fuck(self):

        self.add_Noise()
        self.add_multiple_Gaussians()
    
    def unfuck(self):

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

    
class Plot:
  
    def __init__(self):
             
        self.ylim = -0.5,3
        self.line = plt.axhline(Signal_X.Threashold, color = "red",linestyle='dashed')

    def draw_current_Threashold(self,signal):
        
        self.line.remove()
        self.line = plt.axhline(signal.Threashold, color = "red",linestyle='dashed')

    def draw_elvaluation_lines(self,signal):
        
        plt.axhline(signal.Threashold, color = "red")
        plt.axvline(signal.x_retrieve_start, color = "red")
        plt.axvline(signal.x_retrieve_end, color = "red")

    def draw_text(self,signal):

        if signal.x_retrieved == None:
            plt.text(0.1,3.1," X: "+ "failed", fontsize=12) 
        else:
            plt.text(0.1,3.1," X: "+ str(int(signal.x_retrieved))+" +- "+str(int(signal.x_retrieved_uncertainty)), fontsize=12) 
            #print(coordinates[0]-x_retrieved)
        
        plt.text(0.1,3.3," Average over : "  + str(int(signal.Average_Spectra)) + " Spectra", fontsize=12) 

    def plot_signal(self,signal):
        plt.ylim(self.ylim)
        plt.plot(np.arange(0,signal.X),signal.Y_mean, color = "black")

    def pause(self):
        plt.pause(0.01)

    def clear(self):
        plt.clf()


Signal_X = Signal(450,450)
Signal_Y = Signal(300,200)

Plot_X = Plot()
Plot_Y = Plot()



def check_input():

    
    if keyboard.is_pressed('up'):
            Signal_X.Threashold += 0.03
    
    if keyboard.is_pressed('down'):
            Signal_X.Threashold -= 0.03
    
    if keyboard.is_pressed('right'):
            Signal_X.Average_Spectra += 1
    
    if keyboard.is_pressed('left'):
            if Signal_X.Average_Spectra > 1:
                Signal_X.Average_Spectra -= 1
    
    if keyboard.is_pressed('P'):
            Signal_Y.Threashold += 0.03
    
    if keyboard.is_pressed('Ö'):
            Signal_Y.Threashold -= 0.03

    if keyboard.is_pressed('Ä'):
            Signal_Y.Average_Spectra += 1
    
    if keyboard.is_pressed('L'):
            if Signal_Y.Average_Spectra > 1:
                Signal_Y.Average_Spectra -= 1



i = 0
while True:  # making a loop
    
    # Plot X
    plt.figure(1)
    Plot_X.pause()
    Plot_X.draw_current_Threashold(Signal_X) # the last line is removed within the Method 
    
    i += 1

    if i == 10:

        Plot_X.clear()
        Signal_X.analyse()
        Plot_X.draw_elvaluation_lines(Signal_X)
        Plot_X.draw_text(Signal_X)
        Plot_X.plot_signal(Signal_X)

    # Plot Y 
    plt.figure(2)
    Plot_Y.draw_current_Threashold(Signal_Y) # the last line is removed within the Method 

    if i == 10:

        Plot_Y.clear()
        Signal_Y.analyse()
        Plot_Y.draw_elvaluation_lines(Signal_Y)
        Plot_Y.draw_text(Signal_Y)
        Plot_Y.plot_signal(Signal_Y)


    if i == 10:
        i = 0    

    check_input()
    

    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break    

plt.show()
