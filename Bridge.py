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

from abc import ABC, abstractmethod
# V Schiff = 5m/s
# V Torpedo 13-20m/s

if __name__ == "__main__":

    # initializing pygame
    pygame.init()

    # Setup serial connection (adjust the port as necessary)
    try:
        ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your port (e.g., '/dev/ttyACM0' on Linux)
    except:
        pass
    
    connected_clients  = []
##### Communication #####

class Server:

    """Class to handle server functions including client connections, receiving and sending messages."""
    def __init__(self, host, port, Controler):
        self.host = host
        self.port = port
        self.Controler = Controler
        self.ship = Controler.ship
        self.connected_clients = []  # Stores (conn, addr) tuples
        self.initialized_clients = {}

        # Start the server and listen for clients
        self.start_server()

    def start_server(self):
        """Sets up the server to accept incoming connections."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print("Server is listening...")

        # Start a thread to accept client connections
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """Accept new clients and start a handler thread for each client."""
        while True:
            conn, addr = self.socket.accept()
            self.connected_clients.append((conn, addr))
            print(f"Client connected from {addr}")

            # Start a new thread to handle each client’s messages
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        """Handles communication with a connected client."""
        try:
            while True:
                data_raw = conn.recv(1024)
                if not data_raw:
                    print(f"Client {addr} disconnected.")
                    break
                

                # Decode and display the message from the client
                data = json.loads(data_raw.decode('utf-8'))
                
                print("Recieved: ", data)

                if data["request"] == "Initialize":

                        for conn, client_addr in self.connected_clients:
                            if client_addr == addr:
                                try:
                                    self.initialized_clients[data["ID"]] = conn
                                    print(data["ID"], "Initialized")

                                except BrokenPipeError:
                                    print(f"Connection with {addr} lost while sending message.")

                if data["ID"] == "Voltarium":
            
                    if data["request"] == "get":
                        # Client requested the game state
                        self.send("Voltarium",self.ship.Reactor.Output)

                    elif data["request"] == "update":
                        
                        self.ship.PowerDistribution = data["data"]
                        
                if data["ID"] == "Console":
            
                    if data["request"] == "get":
                        
                        # Client requested the game state
                        message = []
                        message.append(self.ship.export_to_dict())
                        for i in self.Controler.Enemys:
                            message.append(i.export_to_dict())

                        self.send("Console",message)

                    elif data["request"] == "update":
                        
                        self.ship.PowerDistribution = data["data"]
                        

                    
        
        except ConnectionResetError:
            print(f"Connection with {addr} was reset.")
        finally:
            # Clean up on disconnection
            self.connected_clients.remove((conn, addr))
            conn.close()

    def send(self, ID, message):

        conn = self.initialized_clients[ID]

        try:
            response = json.dumps(message).encode('utf-8')
            conn.sendall(response)
            print(f"Sent message to {ID}: {message}")
        except BrokenPipeError:
            print(f"Connection with {ID} lost while sending message.")
    
    
  

def handle_client(conn, addr,Controler):

    ship = Controler.ship
    Enemys = Controler.Enemys
    Torpedos = Controler.Torpedos
    Detections = Controler.Detections

    global connected_clients

    # Add new connection to the list of clients
    connected_clients.append(conn)

    
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

            if command["ID"] == "Console":
                if command["type"] == "get":
                    print("Console requests Gamestate")
                
                if command["type"] == "update":
                    print("Console wants to update Gamestate")


            if command["ID"] == "Infoscreen1":

                data = [ship.hp,ship.x,ship.y,ship.phi,ship.ruder,ship.v*10,ship.schub,ship.cooldown]
                
                response = json.dumps(data).encode('utf-8')
                conn.sendall(response)

            if command["ID"] == "Infoscreen2":

                data = []
                data.append({"ship_x": ship.x,"ship_y": ship.y, "ship_phi": ship.phi}) 
                for i in Enemys:
                        test = i.uncertaincy
                        extracted = {"Name": i.Name, "x": i.x_detected, "y": i.y_detected, 'uncertainty': i.uncertaincy}
                        
                        data.append(extracted)

                       
                
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
                    Controler.ship.v_max = 3 + Controler.PowerDistribution["Engine"]

            if command["ID"] == "Amarium":


                ship.Zeitzünder = command["data"]

    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    finally:
        # Remove client from the list upon disconnection
        connected_clients.remove(conn)
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

def broadcast_update(update_data):
    global connected_clients
    print("connected_clients", connected_clients)
    # Convert the update data to JSON
    update_message = json.dumps({"type": "update", "data": update_data}).encode('utf-8')

    # Send the update to each connected client
    for client in connected_clients[:]:
        try:
            client.sendall(update_message)
        except Exception as e:
            # Remove the client if sending fails
            connected_clients.remove(client)

def Hardware_listener(Controler):
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8').strip()
            
            if message[0:5] == "Ruder":
                ruder = np.round(float(message[6:]))
                Controler.ship.ruder = ruder
                

            if message[0:5] == "Schub":
                schub = np.round(float(message[6:]))
                Controler.ship.schub = schub
                
class Player:
  
    def __init__(self,Controler):
        
        self.Controler = Controler
        self.gamespeed = Controler.gamespeed
        self.Name = "Stingray"
        
        self.Image = 'data/Uboot.png'
        self.scale = (30,40)
        self.hp = 100
        self.Weight = 200 #T
        self.Length = 20 #m
        self.x = 0
        self.y = 0 
        self.phi = 0
        self.ruder = 0
        self.time = 0 
        self.v = 0
        self.schub = 0
        
        self.Reactor = SK36_Stphenson_Reaktor()

        self.PowerDistribution = {"Engine": self.Reactor.Output/3,"Sensorium": self.Reactor.Output/3, "Amarium": self.Reactor.Output/3}
        
        self.Arsenal = Baracuda_Torpedos()
        self.Engine = Aquafine(self)
        
        self.Turret_Angle = 0 
        self.Secondary_Torpedo_cooldown = 0
        self.Primary_Torpedo_Charge = 0
        self.Torpedo_range = 200

        
        Controler.PowerDistribution = {"Engine": self.Reactor.Output/3,"Sensorium": self.Reactor.Output/3, "Amarium": self.Reactor.Output/3}
        
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
                self.schub += 1
            
        elif keys[pygame.K_DOWN]:
            if self.schub > -100:
                self.schub -= 1
            
            
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

    def calculatePosition(self):
        
        
        self.check_input()
        self.phi += 0.006*self.ruder # ~60s für 180°
        self.phi = np.round(self.phi,2)
        

        
        a,k = self.Engine.calculate_acceleration(self.PowerDistribution["Engine"], self.schub)
        
        self.v = self.v + a - (k * self.v) 
               
        self.v = np.round(self.v,5)
        # Player Moveent 
        self.v_x = math.sin(math.radians(self.phi)) * self.v 
        self.v_y = math.cos(math.radians(self.phi)) * self.v
        
        self.x += self.v_x/10
        self.y -= self.v_y/10
        
        self.x = np.round(self.x,3)
        self.y = np.round(self.y,3)
        self.time += 1
        
        if self.time%10 == 1:
            if self.Primary_Torpedo_Charge < self.Arsenal.Required_Charge:
                 self.Primary_Torpedo_Charge += self.PowerDistribution["Amarium"]

        if self.Secondary_Torpedo_cooldown > 0:
            self.Secondary_Torpedo_cooldown -= 1

    def Launch_Primary_Torpedo(self):
        
        if self.Primary_Torpedo_Charge >= self.Arsenal.Required_Charge:
            # Deafult Zünder auf 
            Torpedo(self.Controler, self.Arsenal,"Player",self.x, self.y, self.phi, self.Arsenal.v, self.Torpedo_range )
            self.Controler.Torpedo_Launch.play()
            self.Primary_Torpedo_Charge = 0

    def Launch_Secondary_Torpedo(self):
        
        if self.Secondary_Torpedo_cooldown == 0:
            # Deafult Zünder auf 
            phi = self.phi + self.Turret_Angle
            if phi < -180:
                phi = 360 - phi 
            
            Torpedo(self.Controler, "Player", self.x, self.y, phi, 1, self.Torpedo_range )

            self.Secondary_Torpedo_cooldown += 100

    def draw(self,screen):
            
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, -self.phi)
        rot_rect = rot_image.get_rect(center = (500,500))

        screen.blit(rot_image, rot_rect)

    def export_to_dict(self):

        export = {
            "Type": self.Name,
            "Class": "Prototype",
            "Length" : self.Length,
            "Weight" : self.Weight,
            "Reactor": self.Reactor.Name,
            "Arsenal": self.Arsenal.Name,
            "Engine" : self.Engine.Name,
            "Position": (self.x, self.y),
            "Course" : self.phi          
        }

        return export



class Enemy:
  
    def __init__(self,Controler):

        self.ship = Controler.ship
        self.Torpedos = Controler.Torpedos
        self.Detected_Hostile_Torpedos = []
        self.Controler = Controler
        self.Image = 'data/Uboot2.png'
        self.scale = (10/self.Controler.scale,40/self.Controler.scale)
        self.hp = 100
        self.x = 0 #P1[0]
        self.y = 0 #P1[1]
        self.phi = 0
        self.v = 0 
        self.v_x = 0
        self.v_y = 0
        self.Target = 0
        self.mode = "Default"
        self.phi_soll = 0 
        self.Arsenal = Baracuda_Torpedos()
        self.Reactor = M7_Douglas_Reaktor()
        self.Engine = "K734"
        self.v_max = 3 #m/s
        self.Detection_radius_max = 300 #
        self.Detection_radius = 0
        self.Torpedo_Reload_max = 30 #s
        self.Power_Distribution_ist = [30   , 30, 30]
        self.Power_Distribution_soll = [90, 5, 5]
        self.Charge_Weapons = False
        self.Torpedo_Charge = 0
        self.TurnTime = 100 #s
        self.Sound = Controler.Enemy_Motor 
        self.Sound.play(-1)
        self.Sound.set_volume(0)
        self.time = 0
        self.chase_Timer = 0 
        self.Torpedo_timer = 0
        Controler.Enemys.append(self)
        
        
   
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
        
    def ist_an_soll_angleichen(self):
        
        # Passt phi an phi_soll an 

        delta_phi = (self.phi_soll - self.phi + 360) %360
        
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


        
        for i,j in enumerate(self.Power_Distribution_ist):
            
            if j < self.Power_Distribution_soll[i]:
                self.Power_Distribution_ist[i] +=1
            if j > self.Power_Distribution_soll[i]:
                self.Power_Distribution_ist[i] -=1
       
        if self.Charge_Weapons == True:
            self.Torpedo_Charge += self.Power_Distribution_ist[2]*0.01*self.Reactor.Output


        self.v = self.Power_Distribution_ist[0]*0.01*self.v_max

        self.Detection_radius = self.Power_Distribution_ist[1]*self.Reactor.Output *0.01  * 800 + 60 
        
    def initialize_Attack(self):
        
        self.mode = "Player spotted"
        self.Power_Distribution_soll = [30, 30, 30]
        
        self.Target = (self.ship.x,self.ship.y)
        
        # reset the chase timer 
        self.chase_Timer = 500 
        # start the Torpedo Timer 
        if self.Torpedo_timer == 0:
            self.Torpedo_timer = 100
        # later insert call other ships 
        print("Player Spotted at ", self.Target, "initializing Attak")
        for enemy in self.Controler.Enemys:
            if enemy.mode != "Player spotted":
                enemy.initialize_Attack()
    
    def Attack(self):

        self.phi_soll = self.get_angle_towards(self.Target)
        
        if self.Torpedo_Charge > self.Arsenal.Required_Charge: # also alle 10s
            
            angle = self.phi_soll
            
            distance = math.sqrt((math.pow(self.x - self.Target[0],2)) + (math.pow(self.y - self.Target[1],2)))
            
            range = int(distance + np.random.uniform(50, 50))
             
            self.fire_Torpedo(angle,range)
            
        if self.chase_Timer == 0:
            
            self.initialize_default_behavior()

    def fire_Torpedo(self,angle, range):
           
        Torpedo(self.Controler,self.Arsenal,"Enemy", self.x, self.y, angle, self.Arsenal.v, range)
        self.Primary_Torpedo_Charge = 0

    def check_for_Torpedos(self):
        
        calculate_new_course = False 
        
        if len(self.Torpedos) > 0:
            
            for T in self.Torpedos:
                
                if T.Launched_from != "Enemy":
                
                    D_Object = math.sqrt((T.x - self.x) ** 2 + (T.y - self.y) ** 2)  
                    
                    if D_Object < self.Detection_radius:
                        if T not in self.Detected_Hostile_Torpedos:
                            
                            self.Detected_Hostile_Torpedos.append(T)
                            calculate_new_course = True
                    
                    if D_Object > self.Detection_radius:
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
        self.Charge_Weapons = True
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
            

            Explosion_x = x_T + math.sin(math.radians(phi_T)) * v_T * Explosion_t
            Explosion_y = y_T - math.cos(math.radians(phi_T)) * v_T * Explosion_t
            
            Explosions.append((Explosion_x,Explosion_y))
            
            t = Explosion_t
            


        
        velocities = [self.v,self.v/2]  # Speed of the ship in m/s
        angles = np.arange(-180, 180, 45)  # Rudder positions in degrees
        
        

        distances = []

        for angle in angles:
            for v in velocities:
                distance_local = 0 
                for circle in Explosions:
                    delta_phi = np.radians(angle)  # Convert rudder angle to radians
                    if angle != 0:  # Avoid division by zero for zero angle
                        omega = delta_phi / self.TurnTime # Angular velocity
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
                
                distances.append((angle,v, distance_local))

        distances = np.array(distances)
        best_angle = distances[np.argmax(distances[:,2]), 0]  # Angle corresponding to the minimum exit time
        best_velocity = distances[np.argmax(distances[:, 2]), 1]
        distance = distances[np.argmax(distances[:, 2]), 2]
        self.phi_soll = best_angle
        self.v = best_velocity
        
        print(f'Best Rudder Position: {best_angle}° with v: {best_velocity} resulting distance: {distance:.2f} .')
    
    def initialize_counter_strike(self):

        self.Charge_Weapons = True
        self.mode = "Counter-Strike"
        print("Inizialising counter Attack")
        self.Power_Distribution_soll = [30, 30, 30]
        
        self.chase_Timer = 120

        actual_distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))
        uncertainty_factor = actual_distance/10
        
        
        
        rough_Player_x = np.random.uniform(self.ship.x - uncertainty_factor , self.ship.x + uncertainty_factor)
        rough_Player_y = np.random.uniform(self.ship.y - uncertainty_factor , self.ship.y + uncertainty_factor)

        self.Target = (rough_Player_x, rough_Player_y)
        print("Targeting: ", self.Target)
        # launch a torpedo
        for enemy in self.Controler.Enemys:
            if enemy.mode != "Counter-Strike":
                enemy.initialize_counter_strike()
        self.phi_soll = self.get_angle_towards(self.Target)
    
    def counter_strike(self):
        
        if self.Torpedo_Charge > self.Arsenal.Required_Charge:
            print("Launching Counter Torpedo")

            angle = self.get_angle_towards((self.Target[0],self.Target[1]))
            
            range = int(350)
            self.fire_Torpedo(angle,range)
            

        if self.chase_Timer == 0:
            self.initialize_default_behavior()      

    def check_for_Player(self):
        
        D_Object = math.sqrt((self.ship.x - self.x) ** 2 + (self.ship.y - self.y) ** 2)  
        # Sound anpassen 
        
        a =  max( -D_Object/1000 + 1, 0)       
        self.Sound.set_volume(a/4)

        if D_Object < self.Detection_radius*self.ship.v*10 and self.mode != "Evade" :
            self.initialize_Attack()

    def standard_routine(self):
        
        self.time += 1 
        

        if self.time%10 == 0:           
            
            self.check_for_Torpedos()
            self.check_for_Player()      
            self.ist_an_soll_angleichen()

        if self.chase_Timer > 0:
            self.chase_Timer -=1

        if self.Torpedo_timer > 0:
            self.Torpedo_timer -= 1

        
        
        self.v_x = math.sin(math.radians(self.phi)) * self.v
        self.v_y = math.cos(math.radians(self.phi)) * self.v 
        self.x += self.v_x *0.1
        self.y -= self.v_y *0.1

        if self.mode == "Counter-Strike":
            self.counter_strike()

        if self.mode == "Player spotted":
            
            self.Attack()

    @abstractmethod
    def initialize_default_behavior(self):
        # This method is intended to be implemented by each child
        pass
  
    def draw_Ground_Truth(self,screen):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, -self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+(self.x-self.ship.x)/self.Controler.scale,500+(self.y-self.ship.y)/self.Controler.scale))
        screen.blit(rot_image, rot_rect) 

    def export_to_dict(self):

        export = {
            "Type": self.Name,
            "Class": self.Class,
            "Length" : self.Length,
            "Weight" : self.Weight,
            "Reactor": self.Reactor.Name,
            "Arsenal": self.Arsenal.Name,
            "Engine" : self.Engine,
            "Position": (self.x, self.y),
            "Course" : self.phi          
        }

        return export

class Voyager(Enemy):
    
    def __init__(self,Controler,x,y,phi):
        super().__init__(Controler)

        self.Name = "Voyager"
        self.Class = "Corvette"
        self.Engine = "K734"
        self.v_max = 3
        self.Length = 23
        self.Weight = 30
        self.Arsenal = Baracuda_Torpedos()
        self.Reactor = M7_Douglas_Reaktor()
        

        self.x = x
        self.y = y
        self.course = phi
        self.mode = "Default"


        self.v = 0.2
        self.initialize_default_behavior()

    def initialize_default_behavior(self):
        self.mode = "Default"
        self.v = 0.2
        self.phi_soll = self.course

    def loop(self):
               
        super().standard_routine()

class Transport_Ship(Enemy):
    
    def __init__(self,Controler,x,y,phi):
        super().__init__(Controler)

        self.x = x
        self.y = y
        self.course = phi
        self.mode = "Default"
        self.v = 0.2
        self.initialize_default_behavior()
        

    def initialize_default_behavior(self):
        self.mode = "Default"
        self.v = 0.2
        self.phi_soll = self.course

    def loop(self):
               
        super().standard_routine()

class Patrol_Ship(Enemy):
    
    def __init__(self,Controler,P1,P2):

        super().__init__(Controler)
        self.P1 = P1
        self.P2 = P2
        self.x = P1[0]
        self.y = P1[1]

        self.Target = P2
        
        self.initialize_default_behavior()


    def initialize_default_behavior(self):
        self.mode = "Default"
        self.v = 0.2
        self.Target = self.P2
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

    def loop(self):
               
        super().standard_routine()
        
        if self.mode == "Default" and self.time%10 == 0:
            # Neuen Kurs auf Ziel bestimmen  

            # P1 bzw. P2 als ziel setzten 
            self.Patrol()

class Backup_Enemy:
  
    def __init__(self,Controler):

        self.ship = Controler.ship
        self.Torpedos = Controler.Torpedos
        self.type = type

        self.Detected_Hostile_Torpedos = []
        self.Controler = Controler
        self.Image = 'data/Uboot2.png'
        self.scale = (10/self.Controler.scale,40/self.Controler.scale)
        self.hp = 100
        self.x = 0 #P1[0]
        self.y = 0 #P1[1]
        self.P1 = 0 # P1
        self.P2 = 0 # P2

        self.phi = 0
        self.v_x = 0
        self.v_y =0
        self.mode = "Patroling"
        self.phi_soll = 0 
        self.Target = self.P2
        self.Torpedo_detection_radius = 200
        self.Player_detection_radius = 100

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
        if D_Object < self.Player_detection_radius*self.ship.v:
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
  
    def __init__(self, Controler,Arsenal,Launched_from, x, y ,phi, v,range):

        self.Controler = Controler
        self.ship = Controler.ship

        self.Launched_from = Launched_from
        self.Image = 'data/Torpedo.png'
        self.scale = (10/self.Controler.scale,10/self.Controler.scale)
        self.x = x
        self.y = y 
        self.phi = phi
        self.v = Arsenal.v
        self.Explosion_Radius = Arsenal.Explosion_Radius
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
    
    def explode(self):
        
        # Es wird hier zwei mal die Distanz berechnet geht besser 
        for j,i in enumerate(self.Controler.Enemys):

            distance = math.sqrt((math.pow(self.x - i.x,2)) + (math.pow(self.y - i.y,2)))
            # Berechnung der Projezierten fläche zum Torpedo könnte man auch als LUT machen 
            
            if distance > self.Explosion_Radius*2:
                damage = 0 
                i.hp -= damage
            elif distance < self.Explosion_Radius:
                damage = 100
                i.hp -= damage
            else:
                damage = -1.2*distance+130
                i.hp -= damage
            
            
        # check for colision with player
        distance = math.sqrt((math.pow(self.x - self.ship.x,2)) + (math.pow(self.y - self.ship.y,2)))

        if distance > self.Explosion_Radius*2:
            damge = 0 
            #i.hp -= damage
        elif distance < self.Explosion_Radius:
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
                
        self.x += self.v_x*0.1
        self.y -= self.v_y*0.1

        self.time += 1
               
        if  self.time*self.v > self.range*10:
            self.explode()

    def draw(self):
  
        Image = pygame.image.load(self.Image)
        Image = pygame.transform.scale(Image, (self.scale[0]/self.Controler.scale,self.scale[1]/self.Controler.scale))
        rot_image = pygame.transform.rotate(Image, self.phi)#rot_image = pygame.transform.rotate(Image, -instance.phi_detected)
        rot_rect = rot_image.get_rect(center = (500+(self.x-self.ship.x)/self.Controler.scale,500+(self.y-self.ship.y)/self.Controler.scale))
        self.Controler.screen.blit(rot_image, rot_rect) 

class Baracuda_Torpedos:

    def __init__(self,):

        self.Name = "Baraccuda"
        self.v = 10 #m/s
        self.Required_Charge = 30 #kJ
        self.Explosion_Radius = 30 #m  
     
class M7_Douglas_Reaktor:

    def __init__(self,):

        self.Name = "M7 Douglas"
        self.Output = 1 #kW

class SK36_Stphenson_Reaktor:

    def __init__(self,):

        self.Name = "SK36 Stphenson"
        self.Output = 3 #kW

class Aquafine:

    def __init__(self,Ship):

        self.Name = "Aquafine"
        self.a = 0.03
        self.c = (Ship.Weight/200)*(Ship.Length/20)
        self.a_max = self.a/self.c
        self.Max_Speed = 10 #m/s 
        self.Max_Bedarf = 3 #kW
        self.Eingangsleistung = Ship.PowerDistribution["Engine"]
        


    def calculate_acceleration(self, Eingangsleistung, Schub):
        
        
        Max_Speed_Local = max((min(Eingangsleistung/self.Max_Bedarf,1)) *self.Max_Speed,0.001)
        
       
        k = self.a_max/Max_Speed_Local
        
        a_local = Schub *0.01 * self.a_max

        
        return a_local,k

class detection:
  
    def __init__(self,Controler, x,y,radius,time):
        self.Controler = Controler
        self.x = x
        self.y = y
        self.radius = radius       
        self.transparency = time

    def draw(self,ship,screen):
         
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        
        # pygame.draw.circle(circle, (0, 255, 0,self.transparency), (self.radius, self.radius), self.radius, 2) - draw only outline 
        pygame.draw.circle(circle, (0, 255, 0,self.transparency), (self.radius, self.radius), self.radius)
        screen.blit(circle, (500+(self.x-ship.x -self.radius)/self.Controler.scale, 500+(self.y-ship.y-self.radius)/self.Controler.scale))
        
        self.transparency -= 1

class Dummy_Sensorium:
    
    def __init__(self,Controler):

        self.Enemys = Controler.Enemys
        self.Controler = Controler
        self.Player = Controler.ship
        self.Power = Controler.PowerDistribution["Sensorium"]
        self.Range_max = 1000 #m
    def ping(self):
        
        self.Power = self.Controler.PowerDistribution["Sensorium"]

        for i in self.Enemys:

            distance = math.sqrt((math.pow(self.Player.x - i.x,2)) + (math.pow(self.Player.y - i.y,2)))
            Sigma = 0.1*distance/(2*self.Power+0.1)
            I = np.maximum(200 - 0.2*distance/(1.5*(self.Power+0.1)), 0)
            
            x = np.random.normal(i.x, Sigma)
            y = np.random.normal(i.y, Sigma)

            new = detection(self.Controler, x,y,5,I)
            self.Controler.Detections.append(new)

class GameControler:
  
    def __init__(self):
 
        # Sounds
        pygame.mixer.init()

        
        self.Background_Bubbles = pygame.mixer.Sound('./sounds/Background_Bubbles.wav')
        self.Motor = pygame.mixer.Sound('./sounds/Self_Motor.wav')
        self.Sonar = pygame.mixer.Sound('./sounds/Sonar.wav')
        self.Torpedo_Launch = pygame.mixer.Sound('./sounds/Torpedo.wav')
        self.Enemy_Motor = pygame.mixer.Sound('./sounds/Enemy_Ship.wav')


        self.Sonar.play(-1)
        self.Sonar.set_volume(0.3)
        self.Background_Bubbles.play(-1)
        self.Background_Bubbles.set_volume(0)
        self.Motor.play(-1)
        self.Background_Bubbles.set_volume(0)
        self.Torpedo_Launch.set_volume(1)

        


        
        # Creating screen
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Game properties
        self.gamespeed = 1
        self.scale = 1.1
        self.Level = 0
        self.running = True 
        self.daw_Grid = False

        # Clock for controlling the framerate
        self.time = 0 
        self.clock = pygame.time.Clock()
        # Power distribution: 

        


        #Game Entities
        self.ship = Player(self)
        
        self.Enemys = []
        self.Torpedos = []
        self.Detections = []
        # This is not ideal 
        enemy = Enemy(self)#,P1, P2)
        self.Enemys = []
        



        
        # Define Sectors: 
        # Sector 1:
        self.sector_1 = [[-500,500],[-300,-2000]]
        font_path = os.path.join('data/', 'PressStart2P-Regular.ttf')  # Example path
        self.font = pygame.font.Font(font_path, 12)  # Font size can be adjusted

        
        
        
        # Start the game loop
        self.Dummy_Sensorium = Dummy_Sensorium(self)
        threading.Thread(target=Hardware_listener, args=(self,), daemon=True).start()
        #self.add_Patrol_Ship()
        timer = threading.Timer(1, self.Level_1)
        timer.start()

        # Start the server 
        self.server = Server("0.0.0.0", 8080, self)
                
        self.run()

        
    
    def calculate_Points(self,D = 1000):
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

        

        return P1,P2    
        
    def add_Transport_Ship(self,n,  distance = 500):
        
        # Generate a random angle between 0 and 2π radians
        angle = random.uniform(0, 2 * math.pi)
        course = int(random.uniform(0,360))
        # Calculate the new coordinates
        x = int(self.ship.x + distance * math.cos(angle))
        y = int(self.ship.y + distance * math.sin(angle))

        for i in range(n):
            transporter = Voyager(self,x+i*100,y,course)
                  
        return transporter, x,y, course
    
    def add_Patrol_Ship(self):

        P1,P2 = self.calculate_Points()
     
        patroler = Patrol_Ship(self,P1,P2)
      
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
        V = Font.render("V: "+ str(np.round(ship.v,2)), True, color)

        Engine_Power = Font.render("Engine Power: "+ str(np.round(self.ship.PowerDistribution["Engine"],1)), True, color)
        Sensorium_Power = Font.render("Sensorium Power: "+ str(np.round(self.ship.PowerDistribution["Sensorium"],1)), True, color)
        Torpedo_Power = Font.render("Amarium Power: "+ str(np.round(self.ship.PowerDistribution["Amarium"],1)), True, color)

        Turret_Angle = Font.render("Geschütz Winkel: "+ str(np.round(ship.Turret_Angle,1)), True, color)
        Range = Font.render("Reichweite: "+ str(ship.Torpedo_range), True, color)
        
        if ship.Primary_Torpedo_Charge > self.ship.Arsenal.Required_Charge:
            Torpedo_P = Font.render("Primär Torpedo: BEREIT",True ,color)
        else:
            Torpedo_P = Font.render(f"Primär Torpedo: {ship.Primary_Torpedo_Charge}",True ,color)
        '''
        if ship.Primary_Torpedo_Charge < self.ship.Arsenal.Required_Charge:
            Torpedo_S = Font.render(f"Primär Torpedo: {ship.Primary_Torpedo_Charge}",True ,color)
        else:
            Torpedo_S = Font.render("Sekundär Torpedo: - - -",True ,color)
        '''
        
        
        
        # upper left:
        items = [Position, Phi, Ruder]
        text_spacing = np.arange(10,len(items)*30,30)
        for i,j in enumerate(items):

            self.screen.blit(j, (10, text_spacing[i]))        


        # upper right:
        items = [V,Schub]
        text_spacing = np.arange(10,len(items)*30,30)
        for i,j in enumerate(items):

            self.screen.blit(j, (850, text_spacing[i]))   


        # lower left:
        items = [Torpedo_P,Range]
        
        text_spacing = np.arange(10,len(items)*30,30)
        for i,j in enumerate(items):

            self.screen.blit(j, (10,850 + text_spacing[i]))  

        # lower right:
        items = [HP, Engine_Power, Sensorium_Power,Torpedo_Power]
        text_spacing = np.arange(10,len(items)*30,30)
        for i,j in enumerate(items):

            self.screen.blit(j, (750,850 + text_spacing[i])) 
    
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
            
            
        if keys[pygame.K_h]:
            if self.scale > 0.5:
                self.scale -= 0.1
                
        
        if keys[pygame.K_u]:
            if self.gamespeed < 10:
                self.gamespeed += 0.1
                print(self.gamespeed)
       
        if keys[pygame.K_j]:
            if self.gamespeed > 0:
                self.gamespeed -= 0.1
            if self.gamespeed < 1:
                self.gamespeed = 1
                print(self.gamespeed)        

        if keys[pygame.K_p]:
            
            
            for i in self.Enemys:
                pass  

        if keys[pygame.K_l]:
            done = False
            
            if self.daw_Grid == False and done == False:
                self.daw_Grid = True
                done = True
            
            if self.daw_Grid == True and done == False:
                self.daw_Grid = False
                done = True
    
    def next_Level(self):
        
        # Construct the function name
        func_name = f"Level_{self.Level+1}"
        # Use getattr to fetch the function by name and call it
        func = getattr(self, func_name, None)
        if func:
            func()  # Call the function if it exists
        else:
            print(f"No such function: {func_name}")
    
    def Level_1(self):
        self.Level += 1
        n = 1
        ship, x,y, course = self.add_Transport_Ship(n)
        print(f"Level 1 started: {n} ships, course {course}, last seen at {x,y}")
        """
        if "Console" in self.server.initialized_clients:
            message = n,course,x,y
            self.server.send("Console",message)
        """
        
    def Level_2(self):
        print("Level 2")
        self.Level += 1
        ship = self.add_Transport_Ship(2)

    
    def run(self):

        while self.running:

            # Sounds
            a = self.ship.v*10/self.ship.Engine.a_max
            b = max(0.3,a)
            self.Background_Bubbles.set_volume(b)

            self.Motor.set_volume(self.ship.schub/(2* 100))


            self.screen.fill((0, 0, 0))

            self.check_input()
            self.draw_circles()
            if self.daw_Grid == True:
                self.draw_lines()
            self.infoscreen()
            
            # Take care of the Level stuff
            #if self.Enemys == []:
                #self.next_Level()
            #self.spawn_enemys()

            self.ship.calculatePosition()
            self.ship.draw(self.screen)
            if self.ship.hp <= 0:
                self.running = False
                print("Game Over")


            
            for i in self.Enemys:
                i.loop()
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
            
            if self.time%20 == 0:
                self.Dummy_Sensorium.ping()                
            
            pygame.display.update()
            self.time += 1

            if self.time%100 == 0:
                print("Time Passed: ", self.time/10)
            self.clock.tick(10 * self.gamespeed)  # 10 FPS multiplied by the gamespeed factor


if __name__ == "__main__":

    # Start the Controler in a separate thread
    controler = GameControler()

    controler_thread = threading.Thread(target=controler.run)
    controler_thread.start()








