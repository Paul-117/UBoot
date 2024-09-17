import pygame
import math

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Concentric Circles with Lines and Labels")

# Set colors
GREEN = (255,182,65)
WHITE = (255, 255, 255)

# Set circle parameters
radii = [30, 100, 200, 300, 400, 500]
center_x = screen_width // 2
center_y = screen_height // 2
line_width = 1  # Configurable line width

# Set font for displaying radius
font = pygame.font.SysFont(None, 24)

# Main loop
running = True

def draw_circles():
    # Set circle parameters
    radii = [30, 100, 200, 300, 400, 500]
    center_x = screen_width // 2
    center_y = screen_height // 2
    line_width = 2  # Configurable line width

    # Draw concentric circles and label the radii
    for radius in radii:
        # Draw circle
        pygame.draw.circle(screen, GREEN, (center_x, center_y), radius, line_width)
        
        
    # Draw lines from the innermost (50px) to the outermost (500px) circle
    inner_radius = radii[0]  # 50 px
    outer_radius = radii[-1]  # 500 px

    # Horizontal lines (left and right)
    pygame.draw.line(screen, GREEN, (center_x - outer_radius, center_y), (center_x - inner_radius, center_y), line_width)
    pygame.draw.line(screen, GREEN, (center_x + inner_radius, center_y), (center_x + outer_radius, center_y), line_width)
    
    # Vertical lines (top and bottom)
    pygame.draw.line(screen, GREEN, (center_x, center_y - outer_radius), (center_x, center_y - inner_radius), line_width)
    pygame.draw.line(screen, GREEN, (center_x, center_y + inner_radius), (center_x, center_y + outer_radius), line_width)
    
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
        pygame.draw.line(screen, GREEN, (start_x, start_y), (end_x, end_y), line_width)



while running:
    screen.fill((0,0,0))  # Fill background with white color

    draw_circles()

    # Event handling to close the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
