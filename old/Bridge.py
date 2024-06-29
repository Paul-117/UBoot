import socket
import threading
import json
import time

import pygame
import random
import math

# initializing pygame
pygame.init()


def handle_client(conn, addr):
    #print(f"Connected by {addr}")
    # Unterscheidung nach IP einbauen erkennen wer sich verbunden hat und dann nur das schicken was benötigt wird. 
    # Da es erstmal nur den Sensor gibt passen wir alles auf den Sensor an 


    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            # Decode received data
            command = json.loads(data.decode('utf-8'))

            if command["type"] == "get":
                # Client requested the game state
                data = []
                for i in instances:
                    extracted = {"Name": i.Name, "x": i.x, "y": i.y, 'phi': i.phi}
                    data.append(extracted)
                data.append({"ship_x": ship.x,"ship_y": ship.y})
                response = json.dumps(data).encode('utf-8')
                conn.sendall(response)


            elif command["type"] == "update":
                # Client wants to update the game state
                i = 0
                for j in instances: 
                     #print(command['data'])
                     j.x_detected = command["data"][i]["x_detected"]
                     j.y_detected = command["data"][i]["y_detected"]
                     j.uncertaincy = command["data"][i]["uncertaincy"]
                     drawShip_detected(j)
                     drawShip_detected_legacy(j)
                     print(j.x,j.x_detected)
                     print(j.y,j.y_detected)
                     i +=1
      
                conn.sendall(b"Update successful")

        
       
    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    finally:
        conn.close()

def server_program():
    HOST = "0.0.0.0"
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()





##### Game State Modification #####

# Collision Concept
def isCollision(x1, x2, y1, y2):
	distance = math.sqrt((math.pow(x1 - x2,2)) +
						(math.pow(y1 - y2,2)))
	if distance <= 50:
		return True
	else:
		return False
     
def acceleration():
     a = 0.00001
     return a


class Object:
  
    def __init__(self,Name, Image, x,y,phi,v_0,scale,x_detected,y_detected,phi_detected,uncertaincy):

        self.Name = Name
        self.Image = Image
        self.scale = scale
        self.x = x
        self.y = y 
        self.phi = phi
        self.v_x = v_0[0]
        self.v_y = v_0[1]
        self.x_detected = x_detected
        self.y_detected = y_detected
        self.phi_detected = phi_detected
        self.uncertaincy = uncertaincy
        self.cooldown = 1000

    def calculatePosition(self):
         
        self.x += self.v_x
        self.y -= self.v_y
class detection:
  
    def __init__(self,x,y,radius,time):
        detections.append(self)
        self.x = x
        self.y = y
        self.radius = radius
        self.transparency = time

    def draw(self):
         
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        #pygame.draw.circle(circle, (self.transparency, 0, 0, 128), (self.x, self.y), self.radius,2)
        pygame.draw.circle(circle, (250, 0, 0, 128), (self.x, self.y), self.radius,2)
        screen.blit(circle, (self.x, self.y))
        #self.transparency -= 1



def fire(object1,bullet):

    if ship.cooldown == 0:
        v_x = math.sin(math.radians(object1.phi)) *0.3  + object1.v_x
        v_y = math.cos(math.radians(object1.phi)) *0.31  + object1.v_y

        object2 = Object(bullet, object1.x, object1.y, object1.phi, (v_x,v_y), (10,10) )
        instances.append(object2)

        ship.cooldown += 1000



##### Display #####

# creating screen
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.Font('freesansbold.ttf', 20)

detections = []
test_detection = detection(100,100,100,250)
'''
circle = pygame.Surface((100*2, 100*2), pygame.SRCALPHA)
pygame.draw.circle(circle, (255, 0, 0, 128), (200, 200), 100,2)
screen.blit(circle, (200, 200))'''




def drawShip(ship):

    Image = pygame.image.load(ship.Image)
    Image = pygame.transform.scale(Image, ship.scale)
    rot_image = pygame.transform.rotate(Image, -ship.phi)
    rot_rect = rot_image.get_rect(center = (500,500))

    screen.blit(rot_image, rot_rect) 

def drawShip_detected_legacy(instance):

    Image = pygame.image.load(instance.Image)
    Image = pygame.transform.scale(Image, instance.scale)
    rot_image = pygame.transform.rotate(Image, 0)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
    rot_rect = rot_image.get_rect(center = (instance.x-ship.x,instance.y-ship.y))
    screen.blit(rot_image, rot_rect)   
    
def drawShip_detected(instance):
    
    pygame.draw.circle(screen, (255,255,255), (instance.x_detected-ship.x, instance.y_detected-ship.y), instance.uncertaincy/2, 1) #(r, g, b) is color, (x, y) is center, R is radius and w is the thickness of the circle border.
    
    



instances = []
# 



# player
ship = Object('Space Invader','data/Uboot.png', 500,500, 0,(0,0),(10,40),None,None,None,None)
#instances.append(ship)

# enemy 
enemy = Object('Alien','data/Uboot2.png', 800,800, 0,(0.01,0),(10,40),None,None,None,None)
instances.append(enemy)

# projectile 

#bullet = Object('data/bullet.png', 100,200, 0,(0,0),(50,50))


threading.Thread(target=server_program, daemon=True).start()

# game loop
running = True
while running:

    ##### Game state modification #####

    keys = pygame.key.get_pressed()  # Checking pressed keys
    if keys[pygame.K_RIGHT]:
        ship.phi += 0.1
    if keys[pygame.K_LEFT]:
        ship.phi -= 0.1
    if keys[pygame.K_UP]:
         a = acceleration()
    else:
        a = 0 
        
    if keys[pygame.K_SPACE]:
        fire(ship,'data/bullet.png')
    
    # Player Moveent 
    ship.v_x += math.sin(math.radians(ship.phi)) * a
    ship.v_y += math.cos(math.radians(ship.phi)) * a
    
    
    if ship.cooldown > 0:
        ship.cooldown -=1

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    ship.calculatePosition()
    for i in instances:
         i.calculatePosition()
    
  

    ##### Display #####
    
    # RGB
    #screen.fill((0, 0, 0))
    
    drawShip(ship)
    for i in detections:
        i.draw()
        if i.transparency < 1:
            i.remove()
    

              
    
    
    pygame.display.update()

















