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
                    Controler.ship.v_max = 3 + Controler.PowerDistribution["Engine"]

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

class GameControler:
  
    def __init__(self):
 
        
        
        # Start the server in a separate thread, passing the controler as an argument
        threading.Thread(target=server_program, args=(self,), daemon=True).start()
        
        # Creating screen
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Game properties

        self.scale = 1.1
        self.running = True 
        self.daw_Grid = False

        # Clock for controlling the framerate
        self.time = 0 
        self.clock = pygame.time.Clock()

        #Game Entities
        self.Detections = []
        self.Player_Position = (0,0)
        
        font_path = os.path.join('data/', 'PressStart2P-Regular.ttf')  # Example path
        self.font = pygame.font.Font(font_path, 12)  # Font size can be adjusted


        # Start the game loop

        self.run()
    
                  
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
        items = [Turret_Angle, Torpedo_P,Torpedo_S,Range]
        
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

        if keys[pygame.K_p]:
            for i in self.Enemys:
                print(i.x,i.y, i.phi)    

        if keys[pygame.K_l]:
            done = False
            
            if self.daw_Grid == False and done == False:
                self.daw_Grid = True
                done = True
            
            if self.daw_Grid == True and done == False:
                self.daw_Grid = False
                done = True

        
    def run(self):

        while self.running:
            
            self.screen.fill((0, 0, 0))

            self.check_input()
            self.draw_circles()
            if self.daw_Grid == True:
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
                #i.draw_Ground_Truth(self.screen)
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
        

# Start the Controler in a separate thread
controler = GameControler()

controler_thread = threading.Thread(target=controler.run)
controler_thread.start()


#threading.Thread(target=Hardware_listener, daemon=True).start()













