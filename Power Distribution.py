import matplotlib.pyplot as plt
import keyboard
from matplotlib.animation import FuncAnimation

class PowerDistributionManager:
    def __init__(self, input_power=4):
        self.input_power = input_power  # Total input power in MW

        # Subsystems and their initial percentages (representing resistances)
        self.subsystems = {
            'Noise level': 0.25,           # 25%
            'Peak Intensity': 0.25,        # 25%
            'Peak Position Stability': 0.25, # 25%
            'Local Peak Width': 0.25        # 25%
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
        keyboard.on_press_key('up', self.on_up_event)
        keyboard.on_press_key('down', self.on_down_event)

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


# Create an instance of PowerDistributionManager and run the plot
if __name__ == "__main__":
    manager = PowerDistributionManager(4)  # Input power is 4 MW
    ani = FuncAnimation(manager.fig, manager.update_display, frames=100, interval=100, blit=True)
    plt.show()
