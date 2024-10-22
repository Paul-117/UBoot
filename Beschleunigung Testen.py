import numpy as np
import matplotlib.pyplot as plt

# Constants
v_t = 5  # Desired terminal velocity in m/s
a = 0.05  # Choose a drag coefficient
k = a / v_t  # Calculate acceleration based on the terminal velocity
print(k)
dt = 1  # time step
steps = 1200  # number of steps

# Initialize variables
v = np.zeros(steps)  # velocity array
time = np.arange(steps) * dt  # time array

# Iteratively calculate the velocity
for t in range(1, steps):
    v[t] = v[t - 1] + a * dt - (k * v[t - 1] * dt)

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(time, v, label='Velocity over time', color='b')
plt.axhline(y=v_t, color='r', linestyle='--', label='Terminal Velocity (2 m/s)')
plt.title('Velocity vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.grid()
plt.legend()

plt.show()

# Print the chosen parameters
print(f'Chosen parameters: a = {a}, k = {k}')
