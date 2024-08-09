import pygame
import pygame.freetype  # Import the freetype module.
import socket
import json
import time
import numpy as np
import math
import keyboard  # using module keyboard
import threading

pygame.init()

def update_game_state(new_state):
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to Server")
        command = json.dumps({"type": "update","ID": "Amarium", "data": new_state}).encode('utf-8')
        s.sendall(command)
        print("Data sent")

        #s.close()


class Amarium:
  
    def __init__(self):

        self.Timer = 0
        
object = Amarium()
def update_screen():

    screen.fill((0, 102, 0))
    # You can use `render` and then blit the text surface ...
    #color = (255,255,255)
    
    Timer, rect = GAME_FONT.render("Timer: "+ str(int(object.Timer)),  (255,255,255))

    screen.blit(Timer, (10, 10))

    pygame.display.flip()


#infoscreen(5,3,2,7,True)

# creating screen
screen_width = 200
screen_height = 300
screen = pygame.display.set_mode((screen_width, screen_height))
#print(pygame.font.get_fonts())
GAME_FONT = pygame.freetype.SysFont('lucidafaxkursiv', 20)


def check_input():
    global running 
    
    if keyboard.is_pressed('o'):
            object.Timer += 1
            #Signal_Y.Threashold += 0.01
    
    if keyboard.is_pressed('l'):
            object.Timer -= 1
            #Signal_Y.Threashold -= 0.01
            
    if keyboard.is_pressed('q'):
        running = False

    if running == True:
         threading.Timer(0.01, check_input).start()

running = True
threading.Timer(0.01, check_input).start()


while running:

    #print("update requested")
    #game_state = get_game_state()

    update_screen()
    time.sleep(1)
    update_game_state(object.Timer)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

