import numpy as np
import sounddevice as sd
import keyboard  # To detect key presses in real-time

# Parameters
sample_rate = 44100  # Samples per second
base_frequency = 40  # Base frequency of the engine sound (low rumble)
amplitude = 0.2      # Volume of the engine sound
duration = 10        # Duration of the sound buffer for looping

# Generate time values for the buffer
t = np.arange(int(sample_rate * duration)) / sample_rate

# Create the base engine sound using a low-frequency sine wave
base_wave = amplitude * np.sin(2 * np.pi * base_frequency * t)

# Add harmonics to simulate the complex sound of an engine
harmonics = (
    0.5 * np.sin(2 * np.pi * 2 * base_frequency * t) +  # Second harmonic
    0.3 * np.sin(2 * np.pi * 3 * base_frequency * t) +  # Third harmonic
    0.2 * np.sin(2 * np.pi * 4 * base_frequency * t)    # Fourth harmonic
)

# Combine the base wave with its harmonics
engine_sound = base_wave + harmonics

# Add some low-level noise to make the engine sound more natural
noise = 0.02 * np.random.randn(len(t))
engine_sound += noise

# Normalize the engine sound to avoid clipping
engine_sound = engine_sound / np.max(np.abs(engine_sound))

# Define a callback function for real-time audio playback
def callback(outdata, frames, time, status):
    if status:
        print(status)

    # Create a continuous loop of the engine sound
    outdata[:, 0] = engine_sound[:frames]  # Left channel
    outdata[:, 1] = engine_sound[:frames]  # Right channel (stereo output)

# Create a stream with the callback function
stream = sd.OutputStream(channels=2, samplerate=sample_rate, callback=callback)

# Start the stream to play the engine sound
with stream:
    print("Press 'q' to quit the sound.")
    while True:
        if keyboard.is_pressed('q'):  # Press 'q' to stop the engine sound
            break
