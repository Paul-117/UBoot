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
        self.scale = (30,40)
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
        self.Zeitzünder = 200
    
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
        
        if keys[pygame.K_q]:
            self.Launch_Secondary_Torpedo()

        if keys[pygame.K_a]:
            self.Turret_Angle -= 1
            if self.Turret_Angle < -180:
                self.Turret_Angle = 180

        if keys[pygame.K_d]:
            self.Turret_Angle += 1
            if self.Turret_Angle > 180:
                self.Turret_Angle = -180
        
        if keys[pygame.K_w]:
            self.Zeitzünder += 10

        
        if keys[pygame.K_s]:
            if self.Zeitzünder > 0:
                self.Zeitzünder -= 10

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
            Torpedo(self.Controler,self.x, self.y, self.phi, 1, self.Zeitzünder )

            self.Primary_Torpedo_cooldown += 100

    def Launch_Secondary_Torpedo(self):
        
        if self.Secondary_Torpedo_cooldown == 0:
            # Deafult Zünder auf 
            phi = self.phi + self.Turret_Angle
            if phi < -180:
                phi = 360 - phi 
            print(phi)
            Torpedo(self.Controler, self.x, self.y, phi, 1, self.Zeitzünder )

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
        self.x = 0    #P1[0]
        self.y = -300 #P1[1]
        self.P1 = P1
        self.P2 = P2

        self.phi = 0
        self.v_x = 0
        self.v_y =0
        self.mode = "Patroling"
        self.phi_soll = 0 
        self.Target = self.P2
        self.Torpedo_detection_radius = 300
        self.Player_detection_radius = 100

        self.time = 0
        self.time2 = 0 
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
        
        return angle 
        
    def Kurs_anpassen(self):
        
        # wird jeden gamestep ausgeführt 
        #print("soll: ", int(self.phi_soll),"ist: ", int(self.phi))
        delta_phi = self.phi_soll - self.phi
        
        if delta_phi > 0:
            self.phi += 1
        
        if delta_phi < 0:
            self.phi -= 1

        self.v_x = math.sin(math.radians(self.phi)) * self.v
        self.v_y = math.cos(math.radians(self.phi)) * self.v 

    def Initialize_Patrol(self):
        
        self.mode = "Patroling"
        self.Target = self.P2
        self.v = 0.2

    def Patrol(self):
        
        if self.Target == self.P2:

            D_P2 = math.sqrt((self.P2[0] - self.x) ** 2 + (self.P2[1] - self.y) ** 2)
            if D_P2 < 50:
                self.Target = self.P1
                print("Target:",self.P1[0], self.P1[1] )
        if self.Target == self.P1:

            D_P2 = math.sqrt((self.P1[0] - self.x) ** 2 + (self.P1[1] - self.y) ** 2)
            if D_P2 < 50:
                self.Target = self.P2
                print("Target:",self.P2[0], self.P2[1] )
    
    def initialize_Attack(self):
        
        self.mode = "Player spotted"
        
        self.v = 0.4
        self.Target = (self.ship.x,self.ship.y)
        
        # reset self.time for the torpedos 
        self.time = 0 
        # reset the chase timer 
        self.time2 = 0 
        # later insert call other ships 
    
    def Attack(self):

        if self.time%10 == 0: # also alle 10s
            angle = self.phi_soll
            
            distance = math.sqrt((math.pow(self.x - self.Target[0],2)) + (math.pow(self.y - self.Target[1],2)))
            v_torpedo = 1
            Zeitzünder = int(distance/v_torpedo + np.random.uniform(50, 50))

             
            self.fire_Torpedo(angle,Zeitzünder)
        
    def fire_Torpedo(self,angle, Zeitzünder):
           
        Torpedo(self.Controler, self.x, self.y, angle, 1, Zeitzünder)

    def check_for_Torpedos(self):
        torpedos = []
        if len(self.Torpedos) > 0:
            for T in self.Torpedos:

                D_Object = math.sqrt((T.x - self.x) ** 2 + (T.y - self.y) ** 2)  
                if D_Object < self.Torpedo_detection_radius:
                    torpedos.append([T.x,T.y,T.phi])
        
        if (len(torpedos) > 0) :
            self.initialize_Evade(torpedos)
        
        # wenn alle Torpedos weg sind (erst gegenangriff) zurück zum patrollieren
        if len(torpedos) == 0 and self.mode == "Evade":
            
            self.Initialize_Patrol()
        
    def initialize_Evade(self,Torpedos):
        
        self.mode = "Evade"
        angles = []
        self.v = 0.4
        
        for i in Torpedos:
            angles.append(self.get_angle_towards((i[0],i[1])))
            #angles.append(i[2])
        
        evasion_angle = np.mean(angles)
        
        if self.phi - evasion_angle + 90 < self.phi - evasion_angle - 90: 
            self.phi_soll = evasion_angle + 90

        if self.phi - evasion_angle - 90 < self.phi - evasion_angle + 90: 
            self.phi_soll = evasion_angle - 90
        
        print("incoming",evasion_angle,"Evade:", self.phi_soll, "ist", self.phi)
        print("")
        
    def check_for_Player(self):
        
        D_Object = math.sqrt((self.ship.x - self.x) ** 2 + (self.ship.y - self.y) ** 2)  
        if D_Object < self.Player_detection_radius:
            self.initialize_Attack()
        else:
            if self.time2 > 50: # 20s timeout 
                self.Initialize_Patrol()
            
    def calculatePosition(self):

        if self.time%50 == 0:

            self.check_for_Torpedos()
            #self.check_for_Player() 
            pass     
   
        
        
        # Ist an sollwert anpassen 
        self.Kurs_anpassen()
        self.time += 1 
        
        if self.mode == "Patroling":
                    # Neuen Kurs auf Ziel bestimmen  
            if self.time %10 == 0:
                self.phi_soll = self.get_angle_towards(self.Target)
            
            self.Patrol()

        if self.mode == "Player spotted":
            self.time2 += 1
            self.Attack()

          
        
        self.x += self.v_x
        self.y -= self.v_y
        
    def draw_Ground_Truth(self,screen):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, self.scale)
        rot_image = pygame.transform.rotate(Image, -self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+self.x-self.ship.x,500+self.y-self.ship.y))
        screen.blit(rot_image, rot_rect) 

class Torpedo:
  
    def __init__(self,Controler, x, y ,phi, v,Zeitzünder):

        self.Controler = Controler
        self.ship = Controler.ship

        
        self.Image = 'data/Torpedo.png'
        self.scale = (10,10)
        self.x = x
        self.y = y 
        self.phi = phi
        self.v = v
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
        self.x = x
        self.y = y
        self.radius = radius       
        self.transparency = time

    def draw(self,ship,screen):
         
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        #pygame.draw.circle(circle, (self.transparency, 0, 0, 128), (self.x, self.y), self.radius,2)
        
        pygame.draw.circle(circle, (self.transparency, 0, 0, 255), (self.radius, self.radius), self.radius,2)
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
 
        
        
        # Start the server in a separate thread, passing the controler as an argument
        threading.Thread(target=server_program, args=(self,), daemon=True).start()
        
        # Creating screen
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Game properties
        self.gamespeed = 5
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
        self.sector_1 = [[-00,100],[0,-300]]
        self.P1 = (-200,-300)
        self.P2 = (200,-300)
        font_path = os.path.join('data/', 'PressStart2P-Regular.ttf')  # Example path
        self.font = pygame.font.Font(font_path, 12)  # Font size can be adjusted

        self.spawn_enemys = self.call_every(self.add_enemy, 100)  # Call every 40 seconds

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

        print("Patrol Points: ", P1,P2)

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
        #P1,P2 = self.calculate_Points()
        P1 = self.P1
        P2 = self.P2
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
        Zeitzünder = Font.render("Zeitzünder: "+ str(ship.Zeitzünder), True, color)
        
        if ship.Primary_Torpedo_cooldown == 0:
            Torpedo_P = Font.render("Primär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_P = Font.render("Primär Torpedo: - - -",True ,color)
        
        if ship.Secondary_Torpedo_cooldown == 0:
            Torpedo_S = Font.render("Sekundär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_S = Font.render("Sekundär Torpedo: - - -",True ,color)
        
        items = [HP,Position,Ruder,Phi,Ruder,V,Schub,Turret_Angle, Torpedo_P,Torpedo_S,Zeitzünder]
        
        text_spacing = np.arange(10,len(items)*30,30)

        for i,j in enumerate(items):

            self.screen.blit(j, (10, text_spacing[i]))        
    
    def draw_circles(self):
        
        # Set circle parameters
        radii = [30, 100, 200, 300, 400, 500]
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        line_width = 1  # Configurable line width

        # Draw concentric circles and label the radii
        for radius in radii:
            # Draw circle
            pygame.draw.circle(self.screen, (0,255,0), (center_x, center_y), radius, line_width)
            
            
        # Draw lines from the innermost (50px) to the outermost (500px) circle
        inner_radius = radii[0]  # 50 px
        outer_radius = radii[-1]  # 500 px

        # Horizontal lines (left and right)
        pygame.draw.line(self.screen, (0,255,0), (center_x - outer_radius, center_y), (center_x - inner_radius, center_y), line_width)
        pygame.draw.line(self.screen, (0,255,0), (center_x + inner_radius, center_y), (center_x + outer_radius, center_y), line_width)
        
        # Vertical lines (top and bottom)
        pygame.draw.line(self.screen, (0,255,0), (center_x, center_y - outer_radius), (center_x, center_y - inner_radius), line_width)
        pygame.draw.line(self.screen, (0,255,0), (center_x, center_y + inner_radius), (center_x, center_y + outer_radius), line_width)
        
        # Diagonal lines at 45 degrees (top-left to bottom-right and bottom-left to top-right)
        for angle in [45, 135, 225, 315]:
            radian = math.radians(angle)
            
            # Calculate the start points for the inner circle
            start_x = center_x + inner_radius * math.cos(radian)
            start_y = center_y + inner_radius * math.sin(radian)
            
            # Calculate the end points for the outer circle
            end_x = center_x + outer_radius * math.cos(radian)
            end_y = center_y + outer_radius * math.sin(radian)
            
            # Draw the diagonal line
            pygame.draw.line(self.screen, (0,255,0), (start_x, start_y), (end_x, end_y), line_width)

    def run(self):

        while self.running:
            
            self.screen.fill((0, 0, 0))


            self.draw_circles()
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



#threading.Thread(target=Hardware_listener, daemon=True).start()













