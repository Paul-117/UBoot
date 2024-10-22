from pyo import *
import time

# Start the Pyo server
s = Server().boot()
s.start()

# Load a WAV file
wav_file_path = "C:/Users/edinger/Desktop/Python/UBoot/turbine.wav"  # Update this to your WAV file path
sound = SfPlayer(wav_file_path, loop=True)

# Play the sound
sound.out()

# Set initial playback rate
initial_rate = 1.0  # Normal speed
sound.setRate(initial_rate)

# Function to dynamically change playback speed
def change_playback_speed(duration, steps):
    for i in range(steps):
        # Calculate new playback rate
        new_rate = initial_rate + (i / steps)  # Increase rate over time
        sound.setRate(new_rate)  # Set the new rate

        # Sleep for a short duration for each step
        time.sleep(duration / steps)

# Change playback speed over 10 seconds, with 100 steps
change_playback_speed(10, 100)

# Wait a moment before stopping
time.sleep(2)  # Keep the sound playing for a bit longer

# Stop the server
s.stop()
