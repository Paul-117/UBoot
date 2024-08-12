import pygame
import pygame.freetype
import sys

# Initialize Pygame
pygame.init()

# Get information about displays
info = pygame.display.Info()
display_width, display_height = info.current_w, info.current_h

# Screen resolutions (assuming you know these or get them dynamically)
screen1_resolution = (1920, 1080)  # Example resolution for Screen 1
screen2_resolution = (1920, 1080)  # Example resolution for Screen 2

# Create the first application window for Screen 1
screen1 = pygame.display.set_mode(screen1_resolution, pygame.NOFRAME, 0)
pygame.display.set_caption("Application 1")

# Create the second application window for Screen 2
screen2 = pygame.display.set_mode(screen2_resolution, pygame.NOFRAME, 1)
pygame.display.set_caption("Application 2")

# Main loop for the first application
running1 = True
while running1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running1 = False
    screen1.fill((255, 0, 0))  # Red background for demo
    pygame.display.flip()

# Main loop for the second application
running2 = True
while running2:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running2 = False
    screen2.fill((0, 255, 0))  # Green background for demo
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
