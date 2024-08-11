import socket
import threading
import json
import time
import numpy as np
import pygame
import random
import math
import serial
# initializing pygame
pygame.init()

# Setup serial connection (adjust the port as necessary)
ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your port (e.g., '/dev/ttyACM0' on Linux)

##### Communication #####
def handle_client(conn, addr):
    #print(f"Connected by {addr}")
    # Unterscheidung nach IP einbauen erkennen wer sich verbunden hat und dann nur das schicken was benötigt wird. 
    # Da es erstmal nur den Sensor gibt passen wir alles auf den Sensor an 


    try:
        while True:
            data = conn.recv(1024)
            print("data recieved: ", data )
            if not data:
                print("break")
                break

            # Decode received data
            command = json.loads(data.decode('utf-8'))

            if command["ID"] == "Infoscreen1":

                data = [ship.hp,ship.x,ship.y,ship.phi,ship.ruder,ship.v*10,ship.schub,ship.cooldown]
                print(data)
                response = json.dumps(data).encode('utf-8')
                conn.sendall(response)

            if command["ID"] == "Infoscreen2":

                data = []
                data.append({"ship_x": ship.x,"ship_y": ship.y, "ship_phi": ship.phi}) 
                for i in Enemys:
                        test = i.uncertaincy
                        extracted = {"Name": i.Name, "x": i.x_detected, "y": i.y_detected, 'uncertainty': i.uncertaincy}
                        print(data)
                        data.append(extracted)

                       
                print(data)
                response = json.dumps(data).encode('utf-8')
                conn.sendall(response)

            if command["ID"] == "Sensorium":
            
                if command["type"] == "get":
                    # Client requested the game state
                    data = []
                    data.append({"ship_x": ship.x,"ship_y": ship.y})
                    for i in Enemys:
                        extracted = {"x": i.x, "y": i.y}
                        data.append(extracted)
                        

                    for j in Torpedos:
                        extracted = {"x": j.x, "y": j.y}
                        data.append(extracted)
                        
                    
                    response = json.dumps(data).encode('utf-8')
                    conn.sendall(response)


                elif command["type"] == "update":
                    # Client wants to update the game state
                    x = command["data"]["x"]
                    y = command["data"]["y"]
                    u = command["data"]["uncertainty"] # Sind jeweils [int, int,...]
                    
                    for i in range(len(x)):
                        new = detection(x[i],y[i],u[i],100)
                        detections.append(new)

    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    finally:
        print("Connection closed")
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

def infoscreen():

    # You can use `render` and then blit the text surface ...
    #color = (255,255,255)
   
    
    HP, rect = GAME_FONT.render("HP: "+ str(ship.hp),  (255,255,255))
    X, rect = GAME_FONT.render("X: "+ str(ship.x),  (255,255,255))
    Y, rect = GAME_FONT.render("Y: "+ str(ship.y), (255,255,255))
    Phi, rect = GAME_FONT.render("Phi: "+ str(ship.phi),(255,255,255))
    Ruder, rect = GAME_FONT.render("Ruder: "+ str(ship.ruder),(255,255,255))
    V, rect = GAME_FONT.render("V: "+ str(np.round(ship.v*10,2)),  (255,255,255))
    Schub, rect = GAME_FONT.render("Schub: "+ str(ship.schub) + "%",  (255,255,255))
    Torpedo,rect = GAME_FONT.render("Torpedo: "+ str(ship.cooldown), (255,255,255))

    items = [HP,X,Y,Phi,Ruder,V,Schub,Torpedo]
    text_spacing = np.arange(10,len(items)*30,30)

    for i,j in enumerate(items):

        screen.blit(j, (10, text_spacing[i]))

def Hardware_listener():
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f'Received: {message}')
            if message == "Fire":
                ship.Launch_Torpedo()
##### Game State Modification #####
def pol2cart(X, Y, d, phi):
    
    x = X + d * np.sin(math.radians(phi))
    y = Y - d * np.cos(math.radians(phi))
    return (round(x), round(y))
 
class Player:
  
    def __init__(self,Name, Image,hp, x,y,phi,v,scale,x_detected,y_detected,phi_detected,uncertaincy):

        self.Name = Name
        self.Image = Image
        self.scale = scale
        self.hp = hp
        self.x = x
        self.y = y 
        self.phi = phi
        self.ruder = 0
        self.v = v
        self.a = 0 
        self.schub = 0
        self.x_detected = x_detected
        self.y_detected = y_detected
        self.phi_detected = phi_detected
        self.uncertaincy = uncertaincy
        self.cooldown = 0

    def acceleration(self):
     
     a = self.schub * 0.001 # Später hier funktion einfügen 
     
     return a
    
    def check_input(self):
        keys = pygame.key.get_pressed()  # Checking pressed keys

        if keys[pygame.K_RIGHT]:
            if self.ruder < 45:
                self.ruder += 3 # Je schneller das schiff fährt desto besser kann man mit dem ruder navigieren 
        if keys[pygame.K_LEFT]:
            if self.ruder > -45:
                self.ruder -= 3 # Kleine Korrektur düsen damit das schiff nicht bewegungsunfähig bleibt 
        if keys[pygame.K_UP]:
            if self.schub < 100:
                self.schub += 10
            self.a = self.acceleration()
        elif keys[pygame.K_DOWN]:
            if self.schub > -100:
                self.schub -= 1
            self.a = self.acceleration()
            
        if keys[pygame.K_SPACE]:
            ship.Launch_Torpedo()

    def calculatePosition(self):

        self.check_input()
        ship.phi += 0.05*self.v*self.ruder # vektorzerlegung wenn phi = 45 --> naja anyway geht auch so 
        self.phi = np.round(self.phi,2)
        self.v = self.v + self.a - (0.2 * self.v) #0.2 heißt bei 50 schub is a = 0.5 --> vmax = 2.5 damit es sich ausgleicht

        self.v = np.round(self.v,3)
        # Player Moveent 
        self.v_x = math.sin(math.radians(self.phi)) * self.v 
        self.v_y = math.cos(math.radians(self.phi)) * self.v
        
        #print(ship.v_x,ship.v_y)
        if ship.cooldown > 0:
            ship.cooldown -=1

        self.x += self.v_x
        self.y -= self.v_y
        self.x = np.round(self.x,3)
        self.y = np.round(self.y,3)
        
    def Launch_Torpedo(self):
        
        if self.cooldown == 0:
            # Deafult Zünder auf 
            Torpedo("Torpedo",'data/Torpedo.png', self.x, self.y, self.phi, 1, (10,10), self.x, self.y,self.phi, 10, 500 )

            self.cooldown += 50

    def draw(self):
            
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, -self.phi)
        rot_rect = rot_image.get_rect(center = (500,500))

        screen.blit(rot_image, rot_rect)

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
        
        pygame.draw.circle(circle, (self.transparency, 0, 0, 128), (self.radius, self.radius), self.radius,2)
        screen.blit(circle, (500+self.x-ship.x -self.radius, 500+self.y-ship.y-self.radius))
        
        self.transparency -= 1

class Line():

    def __init__(self):
        
        self.x_spacing = np.arange(0,1000,100)
        self.y_spacing = np.arange(0,1000,100)
        print(self.x_spacing)

    def draw(self):
        color = (102,255,178)
        for i in self.y_spacing:

            if i-ship.y > 1000:
                i -=1000
            if i-ship.y < 0:
                i +=1000
            
            
            pygame.draw.line(screen, color, (0, i-ship.y), (1000, i-ship.y))

        for j in self.x_spacing:
                   
            if j-ship.x > 1000:
                j -=1000

            if j-ship.x < 0:
                j +=1000

            pygame.draw.line(screen, color, (j-ship.x, 0), (j-ship.x, 1000))
        
        pygame.display.flip()  

class Torpedo:
  
    def __init__(self, Name, Image, x,y,phi,v,scale,x_detected,y_detected,phi_detected,uncertaincy,Zeitzünder):

        
        self.Name = Name
        self.Image = Image
        self.scale = scale
        self.x = x
        self.y = y 
        self.phi = phi
        self.v = v
        self.v_x = 0
        self.v_y = 0 
        self.x_detected = x_detected
        self.y_detected = y_detected
        self.phi_detected = phi_detected
        self.uncertaincy = uncertaincy
        self.time = 0
        self.Zeitzünder = Zeitzünder
        Torpedos.append(self)
        
    # das geht besser
    def find_itself(self):
        for i,j in enumerate(Torpedos):
            if j.x == self.x and j.y == self.y:
                return j 
    
    def check_for_colision(self):
        
        for j,i in enumerate(Enemys):
            distance = math.sqrt((math.pow(self.x - i.x,2)) + (math.pow(self.y - i.y,2)))
            # Berechnung der Projezierten fläche zum Torpedo könnte man auch als LUT machen 
            delta_phi = self.phi-i.phi
            Projected_length = np.abs(math.sin(math.radians(delta_phi))*50 + math.cos(math.radians(delta_phi))*5)

            if distance < Projected_length:

                self.explode()
            
        # check for colision with player
        distance = math.sqrt((math.pow(self.x - ship.x,2)) + (math.pow(self.y - ship.y,2)))

        delta_phi = self.phi-ship.phi
        Projected_length = np.abs(math.sin(math.radians(delta_phi))*50 + math.cos(math.radians(delta_phi))*5)
        
        if distance < Projected_length:
            self.explode()

    def explode(self):

        # Es wird hier zwei mal die Distanz berechnet geht besser 
        for j,i in enumerate(Enemys):
            distance = math.sqrt((math.pow(self.x - i.x,2)) + (math.pow(self.y - i.y,2)))
            # Berechnung der Projezierten fläche zum Torpedo könnte man auch als LUT machen 
            
            if distance > 100:
                damge = 0 
                #i.hp -= damage
            elif distance < 50:
                damage = 100
                i.hp -= damage
            else:
                damage = -1.2*distance+130
                i.hp -= damage
            
            
        # check for colision with player
        distance = math.sqrt((math.pow(self.x - ship.x,2)) + (math.pow(self.y - ship.y,2)))

        if distance > 100:
            damge = 0 
            #i.hp -= damage
        elif distance < 50:
            damage = 100
            ship.hp -= damage
        else:
            damage = -1.2*distance+130
            ship.hp -= damage

        # remove Torpedo
        k = self.find_itself()
        Torpedos.remove(k)
        del k

    def calculatePosition(self):

        
        self.v_x = math.sin(math.radians(self.phi)) * self.v
        self.v_y = math.cos(math.radians(self.phi)) * self.v  
                
        self.x += self.v_x
        self.y -= self.v_y

        self.time += 1
        
        if self.time > 70: # Sicherheitsabstand 
            self.check_for_colision()
        
        if  self.time == self.Zeitzünder:
            self.explode()

    def draw(self):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+self.x-ship.x,500+self.y-ship.y))
        screen.blit(rot_image, rot_rect) 

class Enemy:
  
    def __init__(self,Name, Image,hp, x,y,phi,v_0,scale,x_detected,y_detected,phi_detected,uncertaincy):

        self.Name = Name
        self.Image = Image
        self.scale = scale
        self.hp = hp
        #self.x = x
        #self.y = y 
        r = 300
        phi = np.random.uniform(0, 360)
        x = -300 #ship.x + r*math.sin(math.radians(phi))
        y = -300 #ship.y + r*math.cos(math.radians(phi))
        self.x = x
        self.y = y
        self.phi = phi
        self.v_x = v_0[0]
        self.v_y = v_0[1]
        self.x_detected = x_detected
        self.y_detected = y_detected
        self.phi_detected = phi_detected
        self.uncertaincy = uncertaincy
        self.time = 90
        Enemys.append(self)
        
    def get_angle_towards_Player(self):
                
        dir_x, dir_y = self.x - ship.x, self.y - ship.y
        angle = (180 / math.pi) * math.atan2(-dir_y, dir_x)+90

        return angle
 
    def change_Movement(self):

        v = np.random.uniform(0,0.5) 

        
        angle = self.get_angle_towards_Player()

        self.phi = np.random.uniform(angle , angle)
        self.v_x = math.sin(math.radians(self.phi)) * v
        self.v_y = math.cos(math.radians(self.phi)) * v 

    def fire_Torpedo(self):
           
           angle = self.get_angle_towards_Player()   
           distance = math.sqrt((math.pow(self.x - ship.x,2)) + (math.pow(self.y - ship.y,2)))
           print("Angle",angle)
           v_torpedo = 1
           Zeitzünder = int(distance/v_torpedo + np.random.uniform(-20, 20))
           #print("Zeitzünder: ",Zeitzünder)
           Torpedo("Torpedo",'data/Torpedo.png', self.x, self.y, self.phi-180, v_torpedo , (10,10), self.x, self.y,self.phi, 10, Zeitzünder)

    def calculatePosition(self):
         
        self.x -= self.v_x
        self.y -= self.v_y

        self.time += 1
        #print(self.time)
        if self.time == 100: 
            print("Movement changed")
            self.change_Movement()
            

        if self.time > 100: 
            print("Torpedo fired")
            self.fire_Torpedo()
            self.time = 0 

    def draw_Ground_Truth(self):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+self.x-ship.x,500+self.y-ship.y))
        screen.blit(rot_image, rot_rect) 

    
##### Display #####

# creating screen
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
#print(pygame.font.get_fonts())
GAME_FONT = pygame.freetype.SysFont('lucidafaxkursiv', 20)
  


# Enemys
Enemys = []

# Background lines
line = Line()   

# Torpedos: 
Torpedos = []

# Detection circles
detections = []


# player
ship = Player('Player','data/Uboot.png', 100,0,0, 0,0,(10,40),None,None,None,None)

#enemy2 = Enemy('Enemy2','data/Uboot2.png',100, -200,300, 0,(0.01,0),(10,40),None,None,None,None)

### Game Loop ###
def Add_enemy():
    enemy = Enemy('Enemy','data/Uboot2.png',100, 0,100, 0,(0.01,0),(10,40),None,None,None,None)

    timer = threading.Timer(5, Add_enemy)
    timer.daemon = True  # Set the thread as a daemon
    #timer.start()


threading.Thread(target=server_program, daemon=True).start()
threading.Thread(target=Hardware_listener, daemon=True).start()
threading.Timer(3, Add_enemy).start()


running = True
while running:

    ##### Display #####
    
    # Refresh the screen 
    screen.fill((0, 0, 102))
    
    #Draw the player 
    ship.calculatePosition()
    ship.draw()
    if ship.hp <= 0:
        running = False
        print("Game Over")


    #Draw the Info screen
    infoscreen()
    
   # Draw the true enemy ships
    for i in Enemys:
        i.calculatePosition()
        i.draw_Ground_Truth()
        if i.hp <= 0:
            Enemys.remove(i)
            del i

    # Draw Detections:
    for j in detections:
        j.draw()
        if j.transparency < 10:
            
            detections.remove(j)
            del j 
    
    # Draw Torpedos
    for k in Torpedos:
        k.calculatePosition()
        k.draw()
    
    # Draw the Background Lines 
    line.draw()


    time.sleep(0.1)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

















