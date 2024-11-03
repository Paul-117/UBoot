import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import keyboard  # using module keyboard
from matplotlib.animation import FuncAnimation

from scipy.optimize import curve_fit 
import matplotlib.pyplot as mpl 
import time, threading
import socket
import json
import keyboard
import numpy as np


def get_game_state():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("connected")
        s.connect((HOST, PORT))
        command = json.dumps({"type": "get","ID": "Voltarium"}).encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        #print(data)
        game_state = json.loads(data.decode('utf-8'))
        #print(f"Current game state: {game_state}")
        print("connection closed")
        #s.close()
        return game_state

def update_game_state(new_state):
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to Server")
        command = json.dumps({"type": "update","ID": "Voltarium", "data": new_state}).encode('utf-8')
        s.sendall(command)
        print("Data sent")

        #s.close()
        
class PowerDistributionManager:
    
    def __init__(self, input_power=4):
        self.input_power = input_power  # Total input power in MW

        # Subsystems and their initial percentages (representing resistances)
        self.subsystems = {
            'Engine': 0.5,           # 25%
            'Sensorium': 0.5,        # 25%
            'Amarium': 0.5, # 25%
          
        }

        self.subsystem_names = list(self.subsystems.keys())
        self.selected_subsystem_idx = 0  # Start with the first subsystem selected
        self.step_size = 0.01  # Step size for percentage adjustment

        # Set up the plot for displaying power distribution
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.fig.patch.set_facecolor('black')
        
        # Set up animation but do not start yet
        self.ani = None
        self.texts = []  # List to hold text objects for blitting

        # Register key event listeners for Tab, Up, and Down keys
        keyboard.on_press_key('tab', self.on_tab_event)
        keyboard.on_press_key('+', self.on_up_event)
        keyboard.on_press_key('-', self.on_down_event)

    def on_tab_event(self, event):
        """Move to the next subsystem."""
        self.selected_subsystem_idx = (self.selected_subsystem_idx + 1) % len(self.subsystem_names)

    def on_up_event(self, event):
        """Increase the percentage of the selected subsystem."""
        selected_subsystem = self.subsystem_names[self.selected_subsystem_idx]
        self.subsystems[selected_subsystem] += self.step_size
        if self.subsystems[selected_subsystem] > 1:
            self.subsystems[selected_subsystem] = 1  # Cap at 100%

    def on_down_event(self, event):
        """Decrease the percentage of the selected subsystem."""
        selected_subsystem = self.subsystem_names[self.selected_subsystem_idx]
        self.subsystems[selected_subsystem] -= self.step_size
        if self.subsystems[selected_subsystem] < 0:
            self.subsystems[selected_subsystem] = 0  # Ensure no negative values

    def calculate_power_distribution(self):
        """
        Calculate power distribution based on resistance.
        - Subsystem percentages represent resistances.
        - Higher percentages get higher power.
        - Subsystems with 0% receive no power.
        """
        total_resistance = sum(self.subsystems.values())
        actual_power = {}

        for subsystem, percentage in self.subsystems.items():
            if percentage == 0:
                actual_power[subsystem] = 0
            else:
                actual_power[subsystem] = (percentage / total_resistance) * self.input_power

        return actual_power

    def get_actual_power(self):
        """
        Maintain compatibility with previous use cases.
        Return the power distributed to each subsystem.
        """
        return self.calculate_power_distribution()  # Use the updated logic to calculate actual power

    def format_display_line(self, subsystem, percentage, power, selected=False):
        """Format the display line for the plot."""
        symbol = "> " if selected else "  "  # Use ">" for selected, " " otherwise
        formatted_line = f"{symbol}{subsystem:<25}{percentage * 100:>6.1f}%   {power:>6.2f} MW"
        return formatted_line

    def update_display(self, frame):
        """Update the display on the plot for each frame of the animation."""
        actual_power = self.get_actual_power()

        self.ax.clear()
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, len(self.subsystems) + 1)
        self.ax.set_facecolor('black')  # Set the background color to black for the axis
        self.ax.axis('off')

        self.texts = []  # Reset the texts list for each frame

        # Display each subsystem with aligned columns for subsystem name, percentage, and power
        for i, (subsystem, power) in enumerate(actual_power.items()):
            percentage = self.subsystems[subsystem]
            selected = i == self.selected_subsystem_idx
            display_line = self.format_display_line(subsystem, percentage, power, selected)
            # Create a new text object for each subsystem
            text = self.ax.text(0.05, len(self.subsystems) - i, display_line, fontsize=12, family="monospace", color='lime')
            self.texts.append(text)  # Store the text object for blitting

        self.ax.set_title(f'Power Distribution of {self.input_power} MW', fontsize=14, color='lime')

        return self.texts  # Return the list of text objects for blitting

running = True
game_state = {"Engine": 3,"Sensorium": 3, "Amarium": 3}

def update_power_distribuion():
    
    global running 
    current_distribution = get_game_state()
    print(current_distribution)
    manager.input_power = sum(current_distribution[0].values())

    power_engine = manager.get_actual_power()["Engine"]
    power_sensorium = manager.get_actual_power()["Sensorium"]
    power_amarium = manager.get_actual_power()["Amarium"]
    new_distribution = {"Engine": power_engine,"Sensorium": power_sensorium, "Amarium": power_amarium}

    update_game_state(new_distribution)  

    if running == True:
         threading.Timer(1, update_power_distribuion).start()

manager = PowerDistributionManager(9)

threading.Timer(1, update_power_distribuion).start()


ani = FuncAnimation(manager.fig, manager.update_display, frames=100, blit=True, interval=100)
plt.show()
