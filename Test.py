import math

def get_angle_towards_Player():
    x = -100       # Target ship x position
    y = 100       # Target ship y position (inverted y-axis)
    ship_x = 0  # Your ship's x position
    ship_y = 0  # Your ship's y position (inverted y-axis)

    # Calculate direction vector from your ship to the target ship
    dir_x, dir_y = x - ship_x, y - ship_y

    # Calculate the angle in degrees
    angle = math.degrees(math.atan2(dir_y, dir_x))
    
    # Adjust the angle to match the standard [0, 360) range
    angle = (angle + 360) % 360
    
    # Adjust the angle to align with expected conventions
    angle = (angle - 90) % 360
    
    print(angle)
    return angle

get_angle_towards_Player()