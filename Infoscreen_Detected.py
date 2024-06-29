import pygame
import pygame.freetype  # Import the freetype module.
import socket
import json
import time
import numpy as np
import math

pygame.init()

def get_game_state():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        command = json.dumps({"type": "get","ID":"Infoscreen2"}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        
        game_state = json.loads(data.decode('utf-8'))
        #print(f"Current game state: {game_state}")
        return game_state



def infoscreen(data):

    screen.fill((0, 102, 0))
    # You can use `render` and then blit the text surface ...
    #color = (255,255,255)
    index,Name,distance, delta_distance, angle, delta_angle = data
    
    NAME, rect = GAME_FONT.render(str(Name), (255,255,255))
    D, rect = GAME_FONT.render("D: "+ str(int(distance)) + "+-" +str(int(delta_distance)),  (255,255,255))
    Phi, rect = GAME_FONT.render("Phi: "+ str(round(angle,1)) + "+-" +str(round(delta_angle,1)),  (255,255,255))

    items = [NAME,D,Phi]
    text_spacing = np.arange(10,len(items)*30,30)
    offset = index*100
    for i,j in enumerate(items):

        screen.blit(j, (10, offset+text_spacing[i]))

    pygame.display.flip()


#infoscreen(5,3,2,7,True)

# creating screen
screen_width = 200
screen_height = 300
screen = pygame.display.set_mode((screen_width, screen_height))
#print(pygame.font.get_fonts())
GAME_FONT = pygame.freetype.SysFont('lucidafaxkursiv', 20)


def calculate_r_phi(X,Y,Phi,x,y,u):

    distance = math.sqrt((math.pow(X - x,2)) + (math.pow(Y - y,2)))
    delta_distance = u
    dir_x, dir_y = x - X, +(Y - y)
    angle = ((180 / math.pi) * math.atan2(-dir_y, dir_x)+90-Phi+360)%360

    if angle > 180:
        angle = -(360-angle)
    delta_angle = math.asin(u/distance)

    return distance, delta_distance, angle, delta_angle
    
    


running = True

while running:

    print("update requested")
    game_state = get_game_state()
    ship_x = game_state[0]["ship_x"]
    ship_y = game_state[0]["ship_y"]
    ship_phi = game_state[0]["ship_phi"]

    if len(game_state) > 1:
        j = 0
        for i in game_state[1:]: # the last one is the ship position
            
            # calculate distance to ship:
            if i["uncertainty"] != None:
                distance, delta_distance, angle, delta_angle = calculate_r_phi(ship_x,ship_y,ship_phi,i["x"],i["y"],i["uncertainty"])
                Name = i["Name"]
                data = [j,Name, distance, delta_distance, angle, delta_angle]
                infoscreen(data)
                j +=1 


    time.sleep(1)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

