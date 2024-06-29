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
        
        game_state = json.loads(data.decode('utf-8'))
        #print(f"Current game state: {game_state}")
        return game_state

def update_game_state(new_state):
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        command = json.dumps({"type": "update","ID": "Sensorium", "data": new_state}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        
        print(data.decode('utf-8'))
### Vereinfachte berechnung ###

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


# Example: Get the current game state
k = 0
while k < 300:
        
    game_state = get_game_state()
        
    new_gamestate = []
    for i in game_state[:-1]: # the last one is the ship position
        
        # calculate distance to ship:
        
        x_detected, y_detected, uncertaincy = retrieve_xy(game_state[-1]["ship_x"], i["x"], game_state[-1]["ship_y"] , i["y"])
        j = {"Name": "UFO","x_detected": x_detected , "y_detected": y_detected,"uncertaincy": uncertaincy}
        new_gamestate.append(j)

    update_game_state(new_gamestate)
    k += 1

    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            
            break  # finishing the loop
    except:
        break 
    
    time.sleep(0.5)
