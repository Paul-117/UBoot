import pygame
pygame.init()
class GameControler:
  
    def __init__(self):
        # Initialize Pygame
        

        # Creating screen
        screen_width = 1000
        screen_height = 1000
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        
        # Game properties
        self.gamespeed = 1
        self.running = True 

        # Clock for controlling the framerate
        self.clock = pygame.time.Clock()

        # Start the game loop
        self.run()

    def run(self):
        while self.running:
            self.screen.fill((0, 0, 102))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            pygame.display.update()

            self.clock.tick(10 * self.gamespeed)  # 10 FPS multiplied by the gamespeed factor


        # Place for game logic and drawing
        
        

Controler = GameControler()
