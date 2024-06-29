import pygame
import random
import math
from pygame import mixer

# initializing pygame
pygame.init()

# creating screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.Font('freesansbold.ttf', 20)

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
     
def drawShip(pos, angle, image):   
    rot_image = pygame.transform.rotate(image, -angle)
    rot_rect = rot_image.get_rect(center = pos)
    screen.blit(rot_image, rot_rect)   

class Object:
  


    def __init__(self, Image, x,y,phi,v_0,scale):

        self.Image = pygame.image.load(Image)
        self.Image = pygame.transform.scale(self.Image, scale)
        self.x = x
        self.y = y 
        self.phi = phi
        self.v_x = v_0[0]
        self.v_y = v_0[1]
        self.cooldown = 1000

    def drawObject(self):
                
        rot_image = pygame.transform.rotate(self.Image, -self.phi)
        rot_rect = rot_image.get_rect(center = (self.x,self.y))
        screen.blit(rot_image, rot_rect)  

    def calculatePosition(self):
         
        self.x += self.v_x
        self.y -= self.v_y

    

def fire(object1,bullet):

    if ship.cooldown == 0:
        v_x = math.sin(math.radians(object1.phi)) *0.3  + object1.v_x
        v_y = math.cos(math.radians(object1.phi)) *0.31  + object1.v_y

        object2 = Object(bullet, object1.x, object1.y, object1.phi, (v_x,v_y), (10,10) )
        instances.append(object2)

        ship.cooldown += 1000
    
 
instances = []
         
# player
ship = Object('data/spaceship.png', 300,500, 0,(0,0),(50,50))
instances.append(ship)

# enemy 
enemy = Object('data/alien.png', 50,100, 0,(0.01,0),(50,50))
instances.append(enemy)
# projectile 

#bullet = Object('data/bullet.png', 100,200, 0,(0,0),(50,50))





def show_phi(x, y, phi):
    phi_ = font.render("Phi:" + str(round(phi,3)), True, (255,255,255))
    x_ = font.render("V_x:" + str(round(ship.v_x,3)), True, (255,255,255))
    y_ = font.render("V_y" + str(round(ship.v_y,3)), True, (255,255,255))
    screen.blit(phi_, (x , y ))
    screen.blit(x_, (x , y+25 ))
    screen.blit(y_, (x , y+50 ))

# game loop
running = True
while running:

    # RGB
    screen.fill((0, 0, 0))
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


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


    for i in instances:
         i.calculatePosition()
         i.drawObject()
    

    show_phi(5,5,ship.cooldown)

    pygame.display.update()
