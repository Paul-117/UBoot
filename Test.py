import pygame

class YourClass:
    def __init__(self):
        self.y_spacing = [100, 200, 300]  # Example y-spacing
        self.x_spacing = [100, 200, 300]  # Example x-spacing

    def draw_dashed_line(self, screen, color, start_pos, end_pos, dash_length=10, width=1):
        """Draws a dashed line from start_pos to end_pos."""
        x1, y1 = start_pos
        x2, y2 = end_pos
        dl = dash_length

        # Calculate total line length
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        dash_count = int(length // dl)

        # Normalize the direction of the line
        x_delta = (x2 - x1) / length
        y_delta = (y2 - y1) / length

        for i in range(0, dash_count, 2):
            start = (x1 + i * dl * x_delta, y1 + i * dl * y_delta)
            end = (x1 + (i + 1) * dl * x_delta, y1 + (i + 1) * dl * y_delta)
            pygame.draw.line(screen, color, start, end, width)

    def draw_lines(self, ship, screen):
        color = (0, 255, 0)
        
        # Draw horizontal dashed lines
        for i in self.y_spacing:
            if i - ship.y > 1000:
                i -= 1000
            if i - ship.y < 0:
                i += 1000

            self.draw_dashed_line(screen, color, (0, i - ship.y), (1000, i - ship.y), dash_length=10, width=1)

        # Draw vertical dashed lines
        for j in self.x_spacing:
            if j - ship.x > 1000:
                j -= 1000
            if j - ship.x < 0:
                j += 1000

            self.draw_dashed_line(screen, color, (j - ship.x, 0), (j - ship.x, 1000), dash_length=10, width=1)

        # Update the display
        pygame.display.flip()

# Example ship class
class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Pygame initialization and screen setup
pygame.init()
screen = pygame.display.set_mode((1000, 1000))

# Create instances of YourClass and Ship
your_class_instance = YourClass()
ship = Ship(x=500, y=500)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill((0, 0, 0))

    # Call draw_lines
    your_class_instance.draw_lines(ship, screen)

    # Refresh the screen
    pygame.display.flip()

# Quit pygame
pygame.quit()
