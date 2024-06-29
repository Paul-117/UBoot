import pygame
import pygame.freetype  # Import the freetype module.
import socket
import json
import time
import numpy as np

pygame.init()

def get_game_state():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        command = json.dumps({"type": "get","ID":"Infoscreen1"}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        
        game_state = json.loads(data.decode('utf-8'))
        #print(f"Current game state: {game_state}")
        return game_state



def infoscreen(data):

    screen.fill((0, 102, 0))
    # You can use `render` and then blit the text surface ...
    #color = (255,255,255)
    hp,x,y,phi,v,ruder,schub,cooldown = data
    
    HP, rect = GAME_FONT.render("HP: "+ str(hp),  (255,255,255))
    X, rect = GAME_FONT.render("X: "+ str(x),  (255,255,255))
    Y, rect = GAME_FONT.render("Y: "+ str(y), (255,255,255))
    Phi, rect = GAME_FONT.render("Phi: "+ str(phi),(255,255,255))
    Ruder, rect = GAME_FONT.render("Ruder: "+ str(ruder),(255,255,255))
    V, rect = GAME_FONT.render("V: "+ str(np.round(v*10,2)),  (255,255,255))
    Schub, rect = GAME_FONT.render("Schub: "+ str(schub) + "%",  (255,255,255))
    Torpedo,rect = GAME_FONT.render("Torpedo: "+ str(cooldown), (255,255,255))

    items = [HP,X,Y,Phi,Ruder,V,Schub,Torpedo]
    text_spacing = np.arange(10,len(items)*30,30)

    for i,j in enumerate(items):

        screen.blit(j, (10, text_spacing[i]))

    pygame.display.flip()


#infoscreen(5,3,2,7,True)

# creating screen
screen_width = 200
screen_height = 300
screen = pygame.display.set_mode((screen_width, screen_height))
#print(pygame.font.get_fonts())
GAME_FONT = pygame.freetype.SysFont('lucidafaxkursiv', 20)



running = True
while running:
    print("update requested")
    a = get_game_state()
    #a = [100, 0.0, 0.0, 0.0, 0, 0.0, 0, 0]
    infoscreen(a)
    print(a)
    time.sleep(1)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

