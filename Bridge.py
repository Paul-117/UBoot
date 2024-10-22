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
import keyboard  # using module keyboard
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
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
            
            if command["ID"] == "Voltarium":
            
                if command["type"] == "get":
                    # Client requested the game state
                    data = []
                    data.append(Controler.PowerDistribution)
                    response = json.dumps(data).encode('utf-8')
                    conn.sendall(response)

                elif command["type"] == "update":
                    # Client wants to update the game state
                    Controler.PowerDistribution = command["data"]

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
        self.v_max = 10
        
        self.schub = 0
        self.Turret_Angle = 0 
        self.Secondary_Torpedo_cooldown = 0
        self.Primary_Torpedo_cooldown = 0
        self.Torpedo_range = 200

    
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
            self.Torpedo_range += 10

        
        if keys[pygame.K_s]:
            if self.Torpedo_range > 0:
                self.Torpedo_range -= 10

    def acceleration(self):
        
        a = self.schub * 0.00005 #keine ahnung passt in etwa 
        return a
    
    def calculatePosition(self):

        self.check_input()
        self.phi += 0.006*self.ruder # ~60s für 180°
        self.phi = np.round(self.phi,2)
        
        a = self.acceleration()
        k = 0.0045/(self.v_max/10)
        print(a,k)

        self.v = self.v + a - (k * self.v) 

        
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
            Torpedo(self.Controler,"Player",self.x, self.y, self.phi, 1, self.Torpedo_range )

            self.Primary_Torpedo_cooldown += 100

    def Launch_Secondary_Torpedo(self):
        
        if self.Secondary_Torpedo_cooldown == 0:
            # Deafult Zünder auf 
            phi = self.phi + self.Turret_Angle
            if phi < -180:
                phi = 360 - phi 
            print(phi)
            Torpedo(self.Controler, "Player", self.x, self.y, phi, 1, self.Torpedo_range )

            self.Secondary_Torpedo_cooldown += 100

    def draw(self,screen):
            
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, -self.phi)
        rot_rect = rot_image.get_rect(center = (500,500))

        screen.blit(rot_image, rot_rect)

class Enemy:
  
    def __init__(self,Controler, P1,P2):

        self.ship = Controler.ship
        self.Torpedos = Controler.Torpedos
        
        self.Detected_Hostile_Torpedos = []
        self.Controler = Controler
        self.Image = 'data/Uboot2.png'
        self.scale = (10/self.Controler.scale,40/self.Controler.scale)
        self.hp = 100
        self.x = P1[0]
        self.y = P1[1]
        self.P1 = P1
        self.P2 = P2

        self.phi = 0
        self.v_x = 0
        self.v_y =0
        self.mode = "Patroling"
        self.phi_soll = 0 
        self.Target = self.P2
        self.Torpedo_detection_radius = 200
        self.Player_detection_radius = 200

        self.time = 0
        self.chase_Timer = 0 
        self.Torpedo_timer = 0
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

        delta_phi = (self.phi_soll - self.phi + 360) %360
        #print(self.phi_soll, self.phi)
         # Determine the shortest turn direction
        if delta_phi > 180:
            delta_phi -= 360  # Adjust for shortest turn direction

        # Apply the turn: increase or decrease the heading
        if delta_phi > 0:
            self.phi += 1  # Turn clockwise
        elif delta_phi < 0:
            self.phi -= 1  # Turn counterclockwise

        # Ensure phi is within [0, 360)
        self.phi = self.phi % 360

        self.v_x = math.sin(math.radians(self.phi)) * self.v
        self.v_y = math.cos(math.radians(self.phi)) * self.v 

    def Initialize_Patrol(self):
        
        self.mode = "Patroling"
        self.Target = self.P2
        self.v = 0.2
        print("Patroling")

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
        print("Player Spotted")
        self.v = 0.3
        self.Target = (self.ship.x,self.ship.y)
        
        # reset the chase timer 
        self.chase_Timer = 500 
        # start the Torpedo Timer 
        self.Torpedo_timer = 100
        # later insert call other ships 
        print(self.Target)
    
    def Attack(self):

        if self.Torpedo_timer == 0: # also alle 10s
            
            angle = self.phi_soll
            
            distance = math.sqrt((math.pow(self.x - self.Target[0],2)) + (math.pow(self.y - self.Target[1],2)))
            v_torpedo = 1
            range = int(distance + np.random.uniform(50, 50))

             
            self.fire_Torpedo(angle,range)
            self.Torpedo_timer = 300 
        
        if self.chase_Timer == 0:
            self.mode = "Patroling"
            self.Initialize_Patrol()

    def fire_Torpedo(self,angle, range):
           
        Torpedo(self.Controler,"Enemy", self.x, self.y, angle, 1, range)

    def check_for_Torpedos(self):
        
        calculate_new_course = False 
        
        if len(self.Torpedos) > 0:
            
            for T in self.Torpedos:
                
                if T.Name != "Enemy":
                
                    D_Object = math.sqrt((T.x - self.x) ** 2 + (T.y - self.y) ** 2)  
                    
                    if D_Object < self.Torpedo_detection_radius:
                        if T not in self.Detected_Hostile_Torpedos:
                            
                            self.Detected_Hostile_Torpedos.append(T)
                            calculate_new_course = True
                    
                    if D_Object > self.Torpedo_detection_radius:
                        if T in self.Detected_Hostile_Torpedos:
                            self.Detected_Hostile_Torpedos.remove(T)   
                            calculate_new_course = True     
        # clear all torpedos from the List that have exploded 
        for i in self.Detected_Hostile_Torpedos:
            if i not in self.Torpedos:
                self.Detected_Hostile_Torpedos.remove(i)
                calculate_new_course = True
        
        if calculate_new_course == True:
            
            if len(self.Detected_Hostile_Torpedos) > 0:
                print("Torpedo detected")
                self.initialize_Evade(self.Detected_Hostile_Torpedos)
                

        # wenn alle Torpedos weg sind (erst gegenangriff) zurück zum patrollieren
        if len(self.Detected_Hostile_Torpedos) == 0 and self.mode == "Evade":
            self.initialize_counter_strike()  

    def initialize_Evade(self,Torpedos):
        
        self.mode = "Evade"
        Explosions = []
        if self.Torpedo_timer == 0:
            self.Torpedo_timer = 50 # fire a counter Torpedo at 300
        
        for T in Torpedos:
        # Define the torpedo's position and heading
            x_T = T.x
            y_T = T.y
            phi_T = T.phi  # Torpedo heading (0 degrees = positive y direction)
            v_T = T.v

            Explosion_t = T.range - T.time*T.v # gamesteps nach denen der Torpedo explodiert 
            print(T.range, T.time, T.v)

            Explosion_x = x_T + math.sin(math.radians(phi_T)) * v_T * Explosion_t
            Explosion_y = y_T - math.cos(math.radians(phi_T)) * v_T * Explosion_t
            
            Explosions.append((Explosion_x,Explosion_y))
            print(Explosions)
            t = Explosion_t
            


        
        velocities = [0.1,0.2,0.3]  # Speed of the ship in m/s
        angles = np.arange(-180, 180, 45)  # Rudder positions in degrees
        
        T = 100  # Time to complete a 180-degree turn in seconds

        distances = []

        for angle in angles:
            for v in velocities:
                distance_local = 0 
                for circle in Explosions:
                    delta_phi = np.radians(angle)  # Convert rudder angle to radians
                    if angle != 0:  # Avoid division by zero for zero angle
                        omega = delta_phi / T  # Angular velocity
                        R = v / omega  # Calculate turning radius

                        # Parametric equations for the trajectory
                        x = self.x + R * (1 - np.cos(omega * t))  # X position as a function of time
                        y = self.y - R * np.sin(omega * t)  # Y position as a function of time
                    else:
                        # If rudder angle is 0, the ship moves in a straight line
                        x = v * t
                        y = np.zeros_like(t)
                    x = self.x + R * (1 - np.cos(omega * t))  # X position as a function of time
                    y = self.y - R * np.sin(omega * t)  # Y position as a function of time
                    # Check when the ship exits the danger zone (circle)
                    distance_local += np.sqrt((x - circle[0])**2 + (y - circle[1])**2)
                    
                # Store the exit time and angle
                #print(angle,v, distance)
                distances.append((angle,v, distance_local))

        distances = np.array(distances)
        best_angle = distances[np.argmax(distances[:,2]), 0]  # Angle corresponding to the minimum exit time
        best_velocity = distances[np.argmax(distances[:, 2]), 1]
        distance = distances[np.argmax(distances[:, 2]), 2]
        self.phi_soll = best_angle
        self.v = best_velocity
        
        print(f'Best Rudder Position: {best_angle}° with v: {best_velocity} resulting distance: {distance:.2f} .')
    
    def initialize_counter_strike(self):

        self.mode = "Counter-Strike"
        print("Inizialising counter Attack")
        self.v = 0.3
        self.chase_Timer = 500
        actual_distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))
        uncertainty_factor = actual_distance/4
        
        
        
        rough_Player_x = np.random.uniform(self.ship.x - uncertainty_factor , self.ship.x + uncertainty_factor)
        rough_Player_y = np.random.uniform(self.ship.y - uncertainty_factor , self.ship.y + uncertainty_factor)

        self.Target = (rough_Player_x, rough_Player_y)
        print("Targeting: ", self.Target)
        # launch a torpedo

        self.phi_soll = self.get_angle_towards(self.Target)
    
    def counter_strike(self):
        
        if self.Torpedo_timer == 0:
            print("Launching Counter Torpedo")

            angle = self.get_angle_towards((self.Target[0],self.Target[1]))
            
            
            range = int(350)
    
            self.fire_Torpedo(angle,range)
            self.Torpedo_timer = 300

        if self.chase_Timer == 0:
            self.mode = "Patroling"
            self.Initialize_Patrol()

    def check_for_Player(self):
        
        D_Object = math.sqrt((self.ship.x - self.x) ** 2 + (self.ship.y - self.y) ** 2)  
        if D_Object < self.Player_detection_radius:
            self.initialize_Attack()
            
    def calculatePosition(self):


        if self.time%10 == 0:

            self.check_for_Torpedos()
            self.check_for_Player()                
        
        if self.time %10 == 0 and self.mode != "Evade":
            self.phi_soll = self.get_angle_towards(self.Target)
            #print(self.phi_soll)
        # Ist an sollwert anpassen 
        self.Kurs_anpassen()
        # Timers anpassen 
        self.time += 1 
        if self.chase_Timer > 0:
            self.chase_Timer -=1

        if self.Torpedo_timer > 0:
            self.Torpedo_timer -= 1
        
        
        if self.mode == "Patroling":
            # Neuen Kurs auf Ziel bestimmen  

            # P1 bzw. P2 als ziel setzten 
            self.Patrol()
        
        
        if self.mode == "Counter-Strike":
            self.counter_strike()

        if self.mode == "Player spotted":
            
            self.Attack()

          
        
        self.x += self.v_x
        self.y -= self.v_y
        
    def draw_Ground_Truth(self,screen):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, -self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+(self.x-self.ship.x)/self.Controler.scale,500+(self.y-self.ship.y)/self.Controler.scale))
        screen.blit(rot_image, rot_rect) 

class Torpedo:
  
    def __init__(self, Controler, Name, x, y ,phi, v,range):

        self.Controler = Controler
        self.ship = Controler.ship

        self.Name = Name
        self.Image = 'data/Torpedo.png'
        self.scale = (10/self.Controler.scale,10/self.Controler.scale)
        self.x = x
        self.y = y 
        self.phi = phi
        self.v = v
        self.v_x = 0
        self.v_y = 0 
        
        self.time = 0
        self.range = range
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
        print(self.x,self.y)
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
        
        if  self.time*self.v > self.range:
            self.explode()

    def draw(self):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+(self.x-self.ship.x)/self.Controler.scale,500+(self.y-self.ship.y)/self.Controler.scale))
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

class GameControler:
  
    def __init__(self):
 
        
        
        # Start the server in a separate thread, passing the controler as an argument
        threading.Thread(target=server_program, args=(self,), daemon=True).start()
        
        # Creating screen
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Game properties
        self.gamespeed = 1
        self.scale = 1.1
        self.running = True 

        # Clock for controlling the framerate
        self.time = 0 
        self.clock = pygame.time.Clock()

        #Game Entities

        self.ship = Player(self)
        self.Enemys = []
        self.Torpedos = []
        self.Detections = []

        # Power distribution: 

        self.PowerDistribution = {"Engine": 3,"Sensorium": 3, "Amarium": 3}

        # Define Sectors: 
        # Sector 1:
        self.sector_1 = [[-1000,1000],[300,-2300]]
        font_path = os.path.join('data/', 'PressStart2P-Regular.ttf')  # Example path
        self.font = pygame.font.Font(font_path, 12)  # Font size can be adjusted

        self.spawn_enemys = self.call_every(self.add_enemy, 100)  # Call every 40 seconds
        self.P1, self.P2 = self.calculate_Points()
        self.add_enemy()
        # Start the game loop
        self.run()
    
    def calculate_Points(self,D = 1200):
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

        Engine_Power = Font.render("Engine Power: "+ str(np.round(self.PowerDistribution["Engine"],1)), True, color)
        Sensorium_Power = Font.render("Sensorium Power: "+ str(np.round(self.PowerDistribution["Sensorium"],1)), True, color)
        Torpedo_Power = Font.render("Amarium Power: "+ str(np.round(self.PowerDistribution["Amarium"],1)), True, color)

        Turret_Angle = Font.render("Geschütz Winkel: "+ str(np.round(ship.Turret_Angle,1)), True, color)
        Range = Font.render("Reichweite: "+ str(ship.Torpedo_range), True, color)
        
        if ship.Primary_Torpedo_cooldown == 0:
            Torpedo_P = Font.render("Primär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_P = Font.render("Primär Torpedo: - - -",True ,color)
        
        if ship.Secondary_Torpedo_cooldown == 0:
            Torpedo_S = Font.render("Sekundär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_S = Font.render("Sekundär Torpedo: - - -",True ,color)
        
        items = [HP,Position,Ruder,Phi,Ruder,V,Schub, Engine_Power, Sensorium_Power,Torpedo_Power, Turret_Angle, Torpedo_P,Torpedo_S,Range]
        
        text_spacing = np.arange(10,len(items)*30,30)

        for i,j in enumerate(items):

            self.screen.blit(j, (10, text_spacing[i]))        
    
    def draw_circles(self):
        # Circle parameters
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        line_width = 1  # Configurable line width

        # Compute the maximum radius that fits in the window based on the scaling factor
        max_radius = (self.screen_width // 2) * self.scale  # Maximum radius in meters

        # Draw a circle at radius 50 (without text)
        radius_50_pixels = 50 / self.scale  # Convert 50 meters to pixels
        pygame.draw.circle(self.screen, (0, 255, 0), (center_x, center_y), int(radius_50_pixels), line_width)

        # Draw circles in steps of 100m, up to the maximum radius (excluding the 50m circle)
        radius_step = 100
        current_radius = radius_step

        last_drawn_radius_pixels = 0  # Variable to store the radius of the last drawn circle (in pixels)

        while current_radius <= max_radius:
            # Convert the radius from meters to pixels based on the scaling factor
            radius_in_pixels = current_radius / self.scale

            # Draw the circle
            pygame.draw.circle(self.screen, (0, 255, 0), (center_x, center_y), int(radius_in_pixels), line_width)

            # Render the radius text (in meters), skipping the 50m circle
            label = self.font.render(f"{current_radius}m", True, (0, 255, 0))  # Green text color
            label_rect = label.get_rect(center=(center_x, center_y - radius_in_pixels))  # Position above each circle
            self.screen.blit(label, label_rect)

            last_drawn_radius_pixels = radius_in_pixels  # Update the last drawn circle radius
            current_radius += radius_step  # Increase radius by 100m each time

        # Draw cross lines only up to the last drawn circle
        inner_radius_pixels = radius_50_pixels  # Lines now start at the 50m circle (converted to pixels)
        outer_radius_pixels = last_drawn_radius_pixels  # Use the radius of the last drawn circle

        # Horizontal lines (left and right)
        pygame.draw.line(self.screen, (0, 255, 0), (center_x - outer_radius_pixels, center_y), (center_x - inner_radius_pixels, center_y), line_width)
        pygame.draw.line(self.screen, (0, 255, 0), (center_x + inner_radius_pixels, center_y), (center_x + outer_radius_pixels, center_y), line_width)

        # Vertical lines (top and bottom)
        pygame.draw.line(self.screen, (0, 255, 0), (center_x, center_y - outer_radius_pixels), (center_x, center_y - inner_radius_pixels), line_width)
        pygame.draw.line(self.screen, (0, 255, 0), (center_x, center_y + inner_radius_pixels), (center_x, center_y + outer_radius_pixels), line_width)

        # Diagonal lines at 45 degrees (top-left to bottom-right and bottom-left to top-right)
        for angle in [45, 135, 225, 315]:
            radian = math.radians(angle)

            # Calculate the start points for the 50m circle
            start_x = center_x + inner_radius_pixels * math.cos(radian)
            start_y = center_y + inner_radius_pixels * math.sin(radian)

            # Calculate the end points for the last drawn circle
            end_x = center_x + outer_radius_pixels * math.cos(radian)
            end_y = center_y + outer_radius_pixels * math.sin(radian)

            # Draw the diagonal line
            pygame.draw.line(self.screen, (0, 255, 0), (start_x, start_y), (end_x, end_y), line_width)
    
    def draw_lines(self):

        x_spacing = np.arange(0,1000,100/self.scale)
        y_spacing = np.arange(0,1000,100/self.scale)

        ship = self.ship
        
        color = (0,150,0)
        
        for i in y_spacing:

            if i-ship.y > 1000:
                i -=1000
            if i-ship.y < 0:
                i +=1000
            
            
            pygame.draw.line(self.screen, color, (0, i-ship.y), (1000, i-ship.y))

        for j in x_spacing:
                   
            if j-ship.x > 1000:
                j -=1000

            if j-ship.x < 0:
                j +=1000

            pygame.draw.line(self.screen, color, (j-ship.x, 0), (j-ship.x, 1000))

    def check_input(self):
        keys = pygame.key.get_pressed()  # Checking pressed keys
        if keys[pygame.K_z]:
            self.scale += 0.1
            print(self.scale)
            
        if keys[pygame.K_h]:
            if self.scale > 0.5:
                self.scale -= 0.1
                print(self.scale)
        
        if keys[pygame.K_u]:
            if self.gamespeed > 0:
                self.gamespeed += 1
                print(self.gamespeed)
       
        if keys[pygame.K_j]:
            if self.gamespeed > 0:
                self.gamespeed -= 1
                print(self.gamespeed)        
        
    def run(self):

        while self.running:
            
            self.screen.fill((0, 0, 0))

            self.check_input()
            self.draw_circles()
            self.draw_lines()
            self.infoscreen()
            
            #self.spawn_enemys()

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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            pygame.display.update()
            self.time += 1

            if self.time%100 == 0:
                print(self.time/10)
            self.clock.tick(10 * self.gamespeed)  # 10 FPS multiplied by the gamespeed factor
        

# Start the Controler in a separate thread
controler = GameControler()

controler_thread = threading.Thread(target=controler.run)
controler_thread.start()


#threading.Thread(target=Hardware_listener, daemon=True).start()













