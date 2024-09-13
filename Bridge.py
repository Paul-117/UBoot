import socket
import threading
import json
import time
import numpy as np
import pygame
import random
import math
import serial
import os

# V Schiff = 5m/s
# V Torpedo 13-20m/s


# initializing pygame
pygame.init()

# Setup serial connection (adjust the port as necessary)
try:
    ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your port (e.g., '/dev/ttyACM0' on Linux)
except:
    pass
##### Communication #####
def handle_client(conn, addr,Controler):

    ship = Controler.ship
    Enemys = Controler.Enemys
    Torpedos = Controler.Torpedos
    Detections = Controler.Detections
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
                    data.append({"ship_x": ship.x,"ship_y": ship.y, "ship_phi": ship.phi})
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
                        Detections.append(new)

            if command["ID"] == "Amarium":


                ship.Zeitzünder = command["data"]

    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    finally:
        print("Connection closed")
        conn.close()

def server_program(controler):
    HOST = "0.0.0.0"
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr, controler)).start()

def Hardware_listener():
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            print(f'Received: {message}')
            if message == "Fire":
                ship.Launch_Torpedo()

class Player:
  
    def __init__(self,Controler):
        
        self.Controler = Controler
        self.gamespeed = Controler.gamespeed
        self.Image = 'data/Uboot.png'
        self.scale = (20,40)
        self.hp = 100
        self.x = 0
        self.y = 0 
        self.phi = 0
        self.ruder = 0
        self.v = 0
        self.a = 0 
        self.schub = 0
        self.Turret_Angle = 0 
        self.Secondary_Torpedo_cooldown = 0
        self.Primary_Torpedo_cooldown = 0
    
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
                self.schub -= 10
            self.a = self.acceleration()
            
        if keys[pygame.K_SPACE]:
            self.Launch_Primary_Torpedo()
        
        if keys[pygame.K_t]:
            self.Launch_Secondary_Torpedo()

        if keys[pygame.K_f]:
            self.Turret_Angle -= 1
            if self.Turret_Angle < -180:
                self.Turret_Angle = 180

        if keys[pygame.K_h]:
            self.Turret_Angle += 1
            if self.Turret_Angle > 180:
                self.Turret_Angle = -180
        
    def acceleration(self):
        
        a = self.schub * 0.0003 # bei schub 100% ist a = 0.3 heißt bei 10FPS  10sek von 0-5m/s (Numerisch berechnert von chat gpt)
        return a
    
    def calculatePosition(self):

        self.check_input()
        self.phi += 0.05*self.v*self.ruder # vektorzerlegung wenn phi = 45 --> naja anyway geht auch so 
        self.phi = np.round(self.phi,2)
        k = 0.06 # = 0.3/5 a_max/v_max

        self.v = self.v + self.a - (k * self.v) 

        
        self.v = np.round(self.v,3)
        # Player Moveent 
        self.v_x = math.sin(math.radians(self.phi)) * self.v 
        self.v_y = math.cos(math.radians(self.phi)) * self.v
        
        self.x += self.v_x
        self.y -= self.v_y
        
        self.x = np.round(self.x,3)
        self.y = np.round(self.y,3)

        #print(ship.v_x,ship.v_y)
        
        if self.Primary_Torpedo_cooldown > 0:
            self.Primary_Torpedo_cooldown -= 1

        if self.Secondary_Torpedo_cooldown > 0:
            self.Secondary_Torpedo_cooldown -= 1

    def Launch_Primary_Torpedo(self):
        
        if self.Primary_Torpedo_cooldown == 0:
            # Deafult Zünder auf 
            Torpedo(self.Controler,"Torpedo",'data/Torpedo.png', self.x, self.y, self.phi, 1, (10,10), 2500 )

            self.Primary_Torpedo_cooldown += 100

    def Launch_Secondary_Torpedo(self):
        
        if self.Secondary_Torpedo_cooldown == 0:
            # Deafult Zünder auf 
            phi = self.phi + self.Turret_Angle
            if phi < -180:
                phi = 360 - phi 
            print(phi)
            Torpedo(self.Controler,"Torpedo",'data/Torpedo.png', self.x, self.y, phi, 1, (10,10), 250 )

            self.Secondary_Torpedo_cooldown += 100

    def draw(self,screen):
            
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, -self.phi)
        rot_rect = rot_image.get_rect(center = (500,500))

        screen.blit(rot_image, rot_rect)

class Enemy:
  
    def __init__(self,Controler, P1,P2):

        self.ship = Controler.ship
        self.Torpedos = Controler.Torpedos
        self.Controler = Controler
        self.Image = 'data/Uboot2.png'
        self.scale = (10,40)
        self.hp = 100
        self.x = P1[0]
        self.y = P1[1]
        self.P1 = P1
        self.P2 = P2

        self.phi = 0
        self.v_x = 0
        self.v_y =0
        self.mode = "Patroling"
        self.Patrol_direction = 1 # -1 to P1, 1 = to P2
        
        self.time = 90
        Controler.Enemys.append(self)
        self.Initialize_Patrol()

        
    def get_angle_towards(self,P):
        
        x = self.x       # Target ship x position
        y = self.y       # Target ship y position (inverted y-axis)
        ship_x = P[0]  # Your ship's x position
        ship_y = P[1]  # Your ship's y position (inverted y-axis)

        # Calculate direction vector from your ship to the target ship
        dir_x, dir_y = x - ship_x, y - ship_y

        # Calculate the angle in degrees
        angle = math.degrees(math.atan2(dir_y, dir_x))
        
        # Adjust the angle to match the standard [0, 360) range
        angle = (angle + 360) % 360
        
        # Adjust the angle to align with expected conventions
        angle = (angle - 90) % 360
        
        self.phi = angle

    def Initialize_Patrol(self):

        if self.Patrol_direction == 1:
            self.get_angle_towards(self.P2)
        if self.Patrol_direction == -1:
            self.get_angle_towards(self.P1)

        self.v = 0.2
        self.v_x = math.sin(math.radians(self.phi)) * self.v
        self.v_y = math.cos(math.radians(self.phi)) * self.v 

    def Patrol(self):

        self.x += self.v_x
        self.y -= self.v_y
        
        if self.Patrol_direction == 1: # going to P2
            D_P2 = math.sqrt((self.P2[0] - self.x) ** 2 + (self.P2[1] - self.y) ** 2)
            if D_P2 < 10:
                self.Patrol_direction = -1
                self.Initialize_Patrol()
        
        if self.Patrol_direction == -1: # going to P2
            D_P1 = math.sqrt((self.P1[0] - self.x) ** 2 + (self.P1[1] - self.y) ** 2)
            if D_P1 < 10:
                self.Patrol_direction = 1
                self.Initialize_Patrol()

    def Attack(self):

        if self.time%100 == 0: # also alle 10s
            P = (self.ship.x,self.ship.y)
            self.get_angle_towards(P)
            self.v_x = math.sin(math.radians(self.phi)) * self.v
            self.v_y = math.cos(math.radians(self.phi)) * self.v 

        if self.time%300 == 0: # also alle 30s
            self.fire_Torpedo()
        
        self.x += self.v_x
        self.y -= self.v_y


    def fire_Torpedo(self):
           
           distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))
           
           v_torpedo = 0.8
           Zeitzünder = int(distance/v_torpedo + np.random.uniform(50, 50))
           #print("Zeitzünder: ",Zeitzünder)
           Torpedo(self.Controler,"Torpedo",'data/Torpedo.png', self.x, self.y, self.phi, v_torpedo , (10,10),Zeitzünder)

    def calculatePosition(self):
         
        if self.mode == "Patroling":
            self.Patrol()

        if self.mode == "Attack":
            
            self.Attack()

        self.time += 1   
        if len(self.Torpedos) > 0:
            if self.mode != "Attack":
                for T in self.Torpedos:

                    D_Object = math.sqrt((T.x - self.x) ** 2 + (T.y - self.y) ** 2)  
                    if D_Object < 200:
                        self.mode = "Attack"
                        print("you made yourself an enemy")
                        self.v = 2
        
        '''
        if self.time > 300: 
            print("Torpedo fired")
            self.fire_Torpedo()
            self.time = 0 
        '''

    def draw_Ground_Truth(self,screen):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, self.phi+90)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+self.x-self.ship.x,500+self.y-self.ship.y))
        screen.blit(rot_image, rot_rect) 


class Torpedo:
  
    def __init__(self,Controler, Name, Image, x,y,phi,v,scale,Zeitzünder):

        self.Controler = Controler
        self.ship = Controler.ship

        self.Name = Name
        self.Image = Image
        self.scale = scale
        self.x = x
        self.y = y 
        self.phi = phi
        self.v = 1.2 # 12m/s
        self.v_x = 0
        self.v_y = 0 
        
        self.time = 0
        self.Zeitzünder = Zeitzünder
        self.Controler.Torpedos.append(self)
        
    # das geht besser
    def find_itself(self):
        for i,j in enumerate(self.Controler.Torpedos):
            if j.x == self.x and j.y == self.y:
                return j 
    
    def check_for_colision(self): # Hier könnte man den Projezierten querschnitt auch einfach rausnehmen 
        
        for j,i in enumerate(self.Controler.Enemys):
            distance = math.sqrt((math.pow(self.x - i.x,2)) + (math.pow(self.y - i.y,2)))
            # Berechnung der Projezierten fläche zum Torpedo könnte man auch als LUT machen 
            delta_phi = self.phi-i.phi
            Projected_length = np.abs(math.sin(math.radians(delta_phi))*50 + math.cos(math.radians(delta_phi))*5)

            if distance < Projected_length:

                self.explode()
            
        # check for colision with player
        distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))

        delta_phi = self.phi-self.ship.phi
        Projected_length = np.abs(math.sin(math.radians(delta_phi))*50 + math.cos(math.radians(delta_phi))*5)
        
        if distance < Projected_length:
            self.explode()

    def explode(self):

        # Es wird hier zwei mal die Distanz berechnet geht besser 
        for j,i in enumerate(self.Controler.Enemys):
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
        distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))

        if distance > 100:
            damge = 0 
            #i.hp -= damage
        elif distance < 50:
            damage = 100
            self.ship.hp -= damage
        else:
            damage = -1.2*distance+130
            self.ship.hp -= damage

        # remove Torpedo
        k = self.find_itself()
        self.Controler.Torpedos.remove(k)
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
        rot_rect = rot_image.get_rect(center = (500+self.x-self.ship.x,500+self.y-self.ship.y))
        self.Controler.screen.blit(rot_image, rot_rect) 

class detection:
  
    def __init__(self,x,y,radius,time):
        Controler.Detections.append(self)
        self.x = x
        self.y = y
        self.radius = radius       
        self.transparency = time

    def draw(self,ship,screen):
         
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        #pygame.draw.circle(circle, (self.transparency, 0, 0, 128), (self.x, self.y), self.radius,2)
        
        pygame.draw.circle(circle, (self.transparency, 0, 0, 128), (self.radius, self.radius), self.radius,2)
        screen.blit(circle, (500+self.x-ship.x -self.radius, 500+self.y-ship.y-self.radius))
        
        self.transparency -= 1

class Line:

    def __init__(self):
        
        self.x_spacing = np.arange(0,1000,100)
        self.y_spacing = np.arange(0,1000,100)


    def draw(self,ship,screen):
        color = (0,150,0)
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
      
class GameControler:
  
    def __init__(self):
 
        # Creating screen
        screen_width = 1000
        screen_height = 1000
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        
        # Game properties
        self.gamespeed = 2
        self.running = True 

        # Clock for controlling the framerate
        self.clock = pygame.time.Clock()

        #Game Entities

        self.ship = Player(self)
        self.line = Line()
        self.Enemys = []
        self.Torpedos = []
        self.Detections = []

        # Define Sectors: 
        # Sector 1:
        self.sector_1 = [[-500,500],[500,-500]]
        self.P1 = (0,0)
        self.P2 = (100,100)
        font_path = os.path.join('data/', 'PressStart2P-Regular.ttf')  # Example path
        self.font = pygame.font.Font(font_path, 12)  # Font size can be adjusted

        self.spawn_enemys = self.call_every(self.add_enemy, 30)  # Call every 40 seconds

        self.add_enemy()
        # Start the game loop
        self.run()
    
    
    def calculate_Points(self,D = 100):
        sector = self.sector_1
        x1 = sector[0][0]
        x2 = sector[0][1]
        y1 = sector[1][0]
        y2 = sector[1][1]

      
        # Sample random first point 
        P1_x = random.randint(x1, x2)
        P1_y = random.randint(y2, y1)

        
        # get valid x:
        x_stop  = P1_x-D
        if x_stop < x1:
            x_stop = x1

        x_start = P1_x + D

        if x_start > x2:
            x_start = x2

        if x_stop-x1 > 0:
            P2_x = random.randint(x1, x_stop)
        else:
            P2_x = random.randint(x_start, x2)

        # get valid y:
        y_stop  = P1_y-D
        if y_stop < y1:
            y_stop = y1

        y_start = P1_y + D

        if y_start > y2:
            y_start = y2

        if y_stop-y1 > 0:
            P2_y = random.randint(y1, y_stop)
        else:
            P2_y = random.randint(y_start, y2)

        P1 = (P1_x,P1_y)
        P2 = (P2_x,P2_y)

        print(P1,P2)

        return P1,P2    
    
    def call_every(self,function_to_call, interval_seconds):
            # Convert seconds to milliseconds
            interval_ms = interval_seconds * 1000
            last_time_called = pygame.time.get_ticks()

            def wrapper():
                nonlocal last_time_called
                current_time = pygame.time.get_ticks()
                if current_time - last_time_called >= interval_ms:
                    function_to_call()
                    last_time_called = current_time

            return wrapper

    def add_enemy(self):
        P1,P2 = self.calculate_Points()
        enemy = Enemy(self,P1, P2)
              
    def infoscreen(self):

        # You can use `render` and then blit the text surface ...
        color = (0,200,0)
        Font = self.font
        ship = self.ship
        HP = Font.render("HP: "+ str(ship.hp), True, color)
        Position = Font.render("X: "+ str(ship.x) +", "+ str(ship.y),True , color)
        Ruder = Font.render("Ruder: "+ str(ship.ruder),True,color)
        Phi = Font.render("Phi: "+ str(ship.phi),True,color)
        Schub = Font.render("Schub: "+ str(ship.schub) + "%", True,color)
        V = Font.render("V: "+ str(np.round(ship.v*10,2)), True, color)
        Turret_Angle = Font.render("Geschütz Winkel: "+ str(np.round(ship.Turret_Angle,1)), True, color)
        
        if ship.Primary_Torpedo_cooldown == 0:
            Torpedo_P = Font.render("Primär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_P = Font.render("Primär Torpedo: - - -",True ,color)
        
        if ship.Secondary_Torpedo_cooldown == 0:
            Torpedo_S = Font.render("Sekundär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_S = Font.render("Sekundär Torpedo: - - -",True ,color)
        
        items = [HP,Position,Ruder,Phi,Ruder,V,Schub,Turret_Angle, Torpedo_P,Torpedo_S]
        
        text_spacing = np.arange(10,len(items)*30,30)

        for i,j in enumerate(items):

            self.screen.blit(j, (10, text_spacing[i]))        
    
    def run(self):

        while self.running:
            
            self.screen.fill((0, 0, 0))



            self.infoscreen()
            
            self.spawn_enemys()

            self.ship.calculatePosition()
            self.ship.draw(self.screen)
            if self.ship.hp <= 0:
                self.running = False
                print("Game Over")


            
            for i in self.Enemys:
                i.calculatePosition()
                i.draw_Ground_Truth(self.screen)
                if i.hp <= 0:
                    self.Enemys.remove(i)
                    del i

            
            for j in self.Detections:
                j.draw(self.ship,self.screen)
                if j.transparency < 10:
                    self.Detections.remove(j)
                    del j 
            
            for k in self.Torpedos:
                k.calculatePosition()
                k.draw()
            
            # Draw the Background Lines 
            self.line.draw(self.ship,self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            pygame.display.update()
            
            self.clock.tick(10 * self.gamespeed)  # 10 FPS multiplied by the gamespeed factor
        


# Start the Controler in a separate thread
controler = GameControler()
controler_thread = threading.Thread(target=controler.run)
controler_thread.start()

# Start the server in a separate thread, passing the controler as an argument
threading.Thread(target=server_program, args=(controler,), daemon=True).start()

#threading.Thread(target=Hardware_listener, daemon=True).start()













