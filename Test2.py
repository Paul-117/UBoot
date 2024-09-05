import pygame
import threading

class Game_Controler:
    def __init__(self):
        screen_width = 1000
        screen_height = 1000
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        self.gamespeed = 1
        self.running = True 
        self.game_step()

    def game_step(self):
        self.screen.fill((0, 0, 102))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        pygame.display.update()

        if self.running:
            threading.Timer(0.1/self.gamespeed, self.game_step).start()

Controler = Game_Controler()
