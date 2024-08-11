import math

def get_angle_towards_Player():
    x = -300  # Target ship x position
    y = 300   # Target ship y position (inverted y-axis)
    ship_x = 0  # Your ship's x position
    ship_y = 0  # Your ship's y position (inverted y-axis)

    # Calculate direction vector from your ship to the target ship
    dir_x, dir_y = x - ship_x, y - ship_y

    # Since y-axis is inverted, negate dir_y
    angle = math.degrees(math.atan2(-dir_y, dir_x))
    
    # Adjust the angle to be within [0, 360) range
    if angle < 0:
        angle += 360

    return angle

a = get_angle_towards_Player()
print(a)