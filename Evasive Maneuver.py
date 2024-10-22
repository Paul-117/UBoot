import numpy as np
import matplotlib.pyplot as plt

# Constants
velocities = [1,2,3]  # Speed of the ship in m/s
rudder_angles = np.arange(-180, 180, 45)  # Rudder positions in degrees
T = 60  # Time to complete a 180-degree turn in seconds
circle_radius = 50
circles = [(30, 70),(-30,100)]

# Time array
t = np.linspace(0, 40, num=100)  # Time from 0 to T seconds
t2 = 30
# Initial position of the ship
x0, y0 = 0, 0

# Variables to store the exit times and corresponding angles
distances = []

# Plotting
plt.figure(figsize=(10, 10))

# Loop over each rudder angle
for angle in rudder_angles:
    for v in velocities:
        distance_local = 0 
        for circle in circles:
            delta_phi = np.radians(angle)  # Convert rudder angle to radians
            if angle != 0:  # Avoid division by zero for zero angle
                omega = delta_phi / T  # Angular velocity
                print(omega)
                R = v / omega  # Calculate turning radius
                print(R)
                # Parametric equations for the trajectory
                x = x0 + R * (1 - np.cos(omega * t))  # X position as a function of time
                y = y0 + R * np.sin(omega * t)  # Y position as a function of time
            else:
                # If rudder angle is 0, the ship moves in a straight line
                x = v * t
                y = np.zeros_like(t)
            x2 = x0 + R * (1 - np.cos(omega * t2))  # X position as a function of time
            y2 = y0 + R * np.sin(omega * t2)  # Y position as a function of time
            # Check when the ship exits the danger zone (circle)
            distance_local += np.sqrt((x2 - circle[0])**2 + (y2 - circle[1])**2)
            
        # Store the exit time and angle
        #print(angle,v, distance)
        distances.append((angle,v, distance_local))
            
        # Plot the trajectory
        plt.plot(x, y, label=f'Rudder Position: {angle}°, v: {v}')

# Initial position of the ship
plt.scatter(x0, y0, color='green', label='Start Position (0,0)', zorder=5)

# Draw the circle representing the danger zone
for circle in circles:
    circle = plt.Circle(circle, circle_radius, color='orange', fill=False, linestyle='--', label='Danger Zone')
    plt.gca().add_artist(circle)

circle = plt.Circle((0,0), 300, color='grey', fill=False, linestyle='--', label='Detection Zone ')
plt.gca().add_artist(circle)
# Title and labels
plt.title('Ship Trajectories for Different Rudder Positions')
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.xlim(-400, 400)  # Adjust limits for visibility
plt.ylim(-400, 400)
plt.axhline(0, color='gray', lw=0.5, ls='--')
plt.axvline(0, color='gray', lw=0.5, ls='--')
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
#print(distances)
# Finding the best angle for fastest exit
distances = np.array(distances)
best_angle = distances[np.argmax(distances[:,2]), 0]  # Angle corresponding to the minimum exit time
distance = distances[np.argmax(distances[:, 2]), 2]
best_velocity = distances[np.argmax(distances[:, 2]), 1]

print(f'Best Rudder Position: {best_angle}° with v: {best_velocity} ^resulting distance: {distance:.2f} .')


plt.show()


