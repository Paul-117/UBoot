import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time

# Load the audio file
rate, data = wav.read("./sounds/Background_Bubbles.wav")


import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Load sound files
sound_1 = pygame.mixer.Sound('./sounds/Background_Bubbles.wav')
sound_2 = pygame.mixer.Sound('./sounds/Torpedo.wav')
sound_3 = pygame.mixer.Sound('./sounds/Torpedo.wav')

# Play the sounds independently
sound_1.play(-1)
sound_2.play(-1)
sound_3.play(-1)

# Set initial volumes (each can have different starting volume)
volume_1 = 0.5
volume_2 = 0.1
volume_3 = 1

# Set initial volumes for each sound
sound_1.set_volume(volume_1)
sound_2.set_volume(volume_2)
sound_3.set_volume(volume_3)

# Adjust the volume dynamically for each sound
for i in range(10):  # Example loop to change volumes in increments
    time.sleep(0.5)  # Wait 0.5 seconds before changing volumes

    # Adjust volume for each sound independently
    volume_1 -= 0.1# min(volume_1 + 0.05, 1.0)  # Increase volume for sound 1
    volume_2 = max(volume_2 - 0.05, 0.0)  # Decrease volume for sound 2
    volume_3 = min(volume_3 + 0.03, 1.0)  # Increase volume for sound 3 slowly

    # Update the volumes of each sound
    sound_1.set_volume(volume_1)
    sound_2.set_volume(volume_2)
    sound_3.set_volume(volume_3)

    # Print the current volume levels for each sound
    print(f"Sound 1 Volume: {volume_1:.2f}")
    print(f"Sound 2 Volume: {volume_2:.2f}")
    print(f"Sound 3 Volume: {volume_3:.2f}")

# Keep the program running until all sounds finish playing
while pygame.mixer.get_busy():
    pygame.time.Clock().tick(10)
