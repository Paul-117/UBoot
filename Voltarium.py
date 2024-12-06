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


class Client:
    """Class to handle client connection, message listening, and message sending."""
    def __init__(self, host, port,Voltarium):

        self.Voltarium = Voltarium
        self.host = host
        self.port = port
        
        self.socket = None

        # Connect to the server on initialization
        self.connect_to_server()

        # Start a thread to listen for incoming messages
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()
        

    def connect_to_server(self):
        """Establish a connection to the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            print("Connected to server")
        except Exception as e:
            print("Error connecting to server:", e)
            self.socket = None

    def listen_for_messages(self):
        """Continuously listens for messages from the server and passes them to the display."""
        if self.socket is None:
            print("Not connected to the server.")
            return

        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    print("Server disconnected.")
                    break
                # Decode the message and pass it to the display
                message = json.loads(data.decode('utf-8'))
                print("Recieved: ", message)
                
                self.Voltarium.input_power = float(message)
                
                
        except Exception as e:
            print("Error receiving data:", e)
        finally:
            self.socket.close()

    def send(self, Message):
        """Send a command to the server with optional data."""
        if self.socket is None:
            print("Not connected to the server.")
            return

        # Prepare the command to send
        command_json = json.dumps(Message).encode('utf-8')

        try:
            self.socket.sendall(command_json)
            
        except Exception as e:
            print("Error sending data:", e)




        
class Voltarium:
    
    def __init__(self, input_power=4):
        self.input_power = input_power  # Total input power in MW
        self.running = True  
        
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

        # Start the Server Stuff
        self.client = Client("127.0.0.1", 8080,self)
        self.client.send({"ID": "Voltarium", "request": "Initialize"})
        time.sleep(3)
        self.client.send({"ID": "Voltarium", "request": "get"})
        self.thread = threading.Thread(target=self.send_distribution_loop, daemon=True)
        self.thread.start()
        

    def send_distribution_loop(self):
        while self.running:
            power_engine = self.get_actual_power()["Engine"]
            power_sensorium = self.get_actual_power()["Sensorium"]
            power_amarium = self.get_actual_power()["Amarium"]
            new_distribution = {
                "Engine": power_engine,
                "Sensorium": power_sensorium,
                "Amarium": power_amarium,
            }
            self.client.send({"ID": "Voltarium", "request": "update", "data": new_distribution})
            time.sleep(3)  # Pause for 3 seconds before the next send
    
    def on_tab_event(self, event):
        """Move to the next subsystem."""
        self.selected_subsystem_idx = (self.selected_subsystem_idx + 1) % len(self.subsystem_names)
    def on_close(self,event):
         
        self.running = False

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


manager = Voltarium(3)
ani = FuncAnimation(manager.fig, manager.update_display, frames=100, blit=True, interval=100)
plt.show()
