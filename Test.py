import matplotlib.pyplot as plt
import numpy as np
import threading
import keyboard


while True:
    b = np.random.uniform(0.1,1)
    a = np.arange(0,10)


    plt.figure(1)
    plt.plot(a,a*b)

    plt.figure(2)
    plt.plot(a,-a*b)
    

    plt.pause(0.1)
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break    

plt.show()