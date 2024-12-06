import numpy as np
import matplotlib.pyplot as plt

# Constants
v_t = 3.33  # Desired terminal velocity in m/s
dt = 1  # time step
steps = 1200  # number of steps
a_values =  np.arange(0.01, 0.1, 0.01)  # Range of 'a' values to test (0.01 to 0.09)

# Prepare the plot
plt.figure(figsize=(10, 5))

# Loop through different 'a' values
for a in a_values:
    k = a / v_t  # Calculate acceleration based on the terminal velocity
    # Initialize variables
    v = np.zeros(steps)  # velocity array
    time = np.arange(steps) * dt  # time array
    
    # Iteratively calculate the velocity
    for t in range(1, steps):
        v[t] = v[t - 1] + a * dt - (k * v[t - 1] * dt)
    
    # Plot the velocity curve for the current 'a'
    plt.plot(time, v, label=f'a = {a:.2f} k = {k:.2f}')

# Add terminal velocity line
plt.axhline(y=v_t, color='r', linestyle='--', label=f'Terminal Velocity ({v_t} m/s)')

# Plot details
plt.title('Velocity vs Time for Different Acceleration Values')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.grid()
plt.legend()
plt.show()
