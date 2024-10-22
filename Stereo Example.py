import numpy as np
import sounddevice as sd
import keyboard  # To detect key presses in real-time

# Parameters
sample_rate = 44100  # Samples per second
frequency = 440.0    # Frequency of the sine wave in Hz
angle = 45           # Initial angle for stereo panning (0 = Left, 90 = Center, 180 = Right)
amplitude = 0.1      # Volume of the sine wave

# Phase accumulator for smooth wave generation
phase = 0

# Define a callback function for real-time audio playback
def callback(outdata, frames, time, status):
    global angle, phase
    if status:
        print(status)

    # Time array for the current audio buffer
    t = (np.arange(frames) + phase) / sample_rate

    # Generate a continuous sine wave
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

    # Calculate stereo panning based on the current angle
    left_volume = np.cos(np.radians(angle))
    right_volume = np.sin(np.radians(angle))

    # Create stereo audio data with current panning settings
    stereo_wave = np.zeros((frames, 2))
    stereo_wave[:, 0] = sine_wave * left_volume   # Left channel
    stereo_wave[:, 1] = sine_wave * right_volume  # Right channel

    # Output the audio data to the sound buffer
    outdata[:] = stereo_wave

    # Update the phase to continue the wave smoothly in the next callback
    phase += frames
    phase %= sample_rate  # Wrap around phase to avoid overflow

# Create a stream with the callback function
stream = sd.OutputStream(channels=2, samplerate=sample_rate, callback=callback)

# Start the stream
with stream:
    print("Use the left and right arrow keys to change the angle of the sound.")
    while True:
        # Adjust the angle based on keyboard input
        if keyboard.is_pressed('left'):
            angle = max(0, angle - 1)  # Decrease the angle, but don't go below 0
        if keyboard.is_pressed('right'):
            angle = min(180, angle + 1)  # Increase the angle, but don't go above 180

        # Print the current angle for feedback
        print(f"Current angle: {angle}°", end='\r')
