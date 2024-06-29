import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import keyboard  # using module keyboard


from scipy.optimize import curve_fit 
import matplotlib.pyplot as mpl 


x_range = 10000
x_pixels = 5000
X = np.linspace(0,x_range,x_pixels)
scale = int(x_pixels/x_range)

# Grundsignal auf dass modulation addiert wird 


def add_Gaussian(X,x,I,sigma):

    Y = I*(2.5*sigma)*stats.norm.pdf(X, x, sigma)

    return Y

def add_Tilt(X,Y,x,sigma,Tilt):
    
    a = np.array(Tilt*X)
    b = np.array( 1*(2.5*sigma)*stats.norm.pdf(X, x, 1000))
    Y +=  a * b
    
    plt.plot(X,a)
    plt.plot(X,b)
    plt.plot(X,a*b, c ='red')
    plt.plot((a * b)/ b)
    
    return Y

def add_multiple_Gaussians(X,Y,x,I,sigma,n):
    
    Y_stack = np.zeros(x_pixels)
    i = 0 
    while i < n:
        I = np.random.uniform(0.1,1)* I
        sigma_local = np.random.uniform(0.1*sigma,0.3*sigma)
        x_local = np.random.uniform(x-sigma,x+sigma)
        Y_local = add_Gaussian(X,x_local,I,sigma_local)
        Y_stack = np.vstack([Y_stack,Y_local])
        #plt.plot(X,Y_local)
        #plt.axvline(x=x_local, color = "red")
        #print(x_local,I,sigma_local)
        i += 1 
    Y += Y_stack[1:].sum(axis = 0)
   
def add_Noise(Y,I):

    Y += np.random.normal(0,I,x_pixels)
    #print(np.random.normal(I,1,x_pixels))

# Let's create a function to model and create data 
def fit_func(x, a, x0, sigma): 
    return a*np.exp(-(x0-x)**2/(2*sigma**2)) 

def fuck_the_Signal(X,Y,coordinates,Noise,sigma,num_Gaussians):
    #r = np.sqrt(coordinates[0]**2+coordinates[1]**2)
    #print("Distance: ",int(r))
    #I = 2-r/5000
    #print("Signal Intensity: ", I)
    I = 1
    add_Noise(Y,Noise)
    #add_Gaussian(X,coordinates[0],I,sigma)
    #Y += add_Gaussian(X,coordinates[0],I,sigma)
    #add_Tilt(X,Y,coordinates[0],sigma*3,5/10000)
    #print(np.max(Y))
    add_multiple_Gaussians(X,Y,coordinates[0],I,sigma,num_Gaussians)
      
def unfuck_the_Signal_Gaussfit(X,Y):
    #print(type(a))
    popt, pcov = curve_fit(fit_func, X,Y,[1,int(X[np.argmax(Y)]),1]) 
    ym = fit_func(X, popt[0], popt[1], popt[2]) 
    
    return ym, popt[1]

def unfuck_the_Signal_Threashold(X,Y,Threashold):
    
    X_above_Threashold = X[Y>Threashold]
    plt.axhline(Threashold, color = "red")
    if len(X_above_Threashold > 2):
        plt.axvline(X_above_Threashold[0], color = "red")
        plt.axvline(X_above_Threashold[-1], color = "red")
        x_retrieved = X_above_Threashold[0] + (X_above_Threashold[-1] - X_above_Threashold[0] )/2
    else:
        x_retrieved = None
        

    #print(X_above_Threashold[-1])
    #print(X_above_Threashold[0])
    
    return x_retrieved
    
def analyse_Signal(coordinates,average_Spectra = 1):
    
    Y_stack = np.zeros(x_pixels)
    i = 0 
    x_fitted = []
    while i < average_Spectra:

        Y = np.zeros(x_pixels)
        fuck_the_Signal(X,Y,coordinates,Noise = 0.01, sigma = 500, num_Gaussians = 3)
        Y_stack = np.vstack([Y_stack,Y])
        #y_fit,x_fit = unfuck_the_Signal(X,Y)
        #x_fitted[0].append(x_fit)
        i += 1

    for y in Y_stack[1:]:
        pass
        #plt.plot(X,y)
        
    Y_mean = np.mean(Y_stack[1:], axis=0)
    x_retrieved = unfuck_the_Signal_Threashold(X,Y_mean,Threashold = 0.2)
    #Y_fit,x_fit = unfuck_the_Signal(X,Y_mean)
    x_fitted.append(x_retrieved)
    
    plt.plot(X,Y_mean,c ="black")
    #plt.plot(X,Y_fit,c ="red")
    #print(np.mean(x_fitted[0]),x_fitted[1][0])
    
    return x_fitted




coordinates = (7000,0)
Threashold = 0.1
average_Spectra = 3
i = 0
line = plt.axhline(Threashold, color = "red")
Y_stack = np.zeros(x_pixels)

while True:  # making a loop
    
    line.remove()
    line = plt.axhline(Threashold, color = "red",linestyle='dashed')

    plt.ylim(-0.5, 2)
    plt.pause(0.1)
    i += 1

    if i == 20:


        Y = np.zeros(x_pixels)
        fuck_the_Signal(X,Y,coordinates,Noise = 0.01, sigma = 300, num_Gaussians = 3) # sigma: im mittel soll der wert 300 daneben liegen 
        Y_stack = np.vstack([Y_stack,Y])

        Y_mean = np.mean(Y_stack, axis=0)
        
        plt.clf()
        
        x_retrieved = unfuck_the_Signal_Threashold(X,Y_mean,Threashold) 


        if x_retrieved == None:
            plt.text(0.1,2," X: "+ "failed", fontsize=12) 
        else:
            plt.text(0.1,2," X: "+ str(int(x_retrieved)), fontsize=12) 

        plt.plot(X,Y_mean, color = "black")

        print(len(Y_stack))
        if len(Y_stack) == average_Spectra:
            Y_stack = np.delete(Y_stack,0,0)
        print(coordinates[0]-x_retrieved)
    if i == 20:
        i = 0    

    if keyboard.is_pressed('up'):
            Threashold += 0.01
    if keyboard.is_pressed('down'):
            Threashold -= 0.01
    


    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break    

plt.show()
'''
x_retrieved = []    

for i in range(1):
    x_retrieved.append(int(analyse_Signal(coordinates)[0])-coordinates[0])
    
#analyse_Signal(coordinates)

print(x_retrieved)

for i in range(len(x_retrieved)):
    
    x_retrieved[i] = np.sqrt(x_retrieved[i]**2)
    
print(np.mean(x_retrieved))

plt.ylim(-0.5, 2)
plt.show()

''' 
