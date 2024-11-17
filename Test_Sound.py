import pyaudio
from pydub import AudioSegment
from threading import Thread
import time
import keyboard  # To handle keypress events

# Function to prevent clipping by normalizing the audio
def normalize_audio(sound):
    # Normalize the sound to -3 dB to avoid clipping
    normalized = sound.normalize()
    return normalized

# Function to play a sound with dynamic volume control and looping
def play_sound(file_path, volume_db=0, loop=False):
    # Load the sound
    sound = AudioSegment.from_wav(file_path)  # Use WAV format for compatibility
    sound = normalize_audio(sound)  # Normalize to avoid clipping
    sound = sound + volume_db  # Apply volume change after normalization

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(sound.sample_width),
        channels=sound.channels,
        rate=sound.frame_rate,
        output=True
    )

    # Playback loop controller
    stop_playback = False

    def play_loop():
        nonlocal sound, stop_playback
        while loop and not stop_playback:
            stream.write(sound.raw_data)
        if not stop_playback:  # Final play when loop stops
            stream.write(sound.raw_data)

    # Start playback in a separate thread
    thread = Thread(target=play_loop)
    thread.start()

    # Function to dynamically adjust volume
    def adjust_volume(new_volume_db):
        nonlocal sound
        # Apply volume change after normalizing again to avoid clipping
        sound = normalize_audio(sound + new_volume_db)

    # Function to stop playback
    def stop():
        nonlocal stop_playback
        stop_playback = True
        thread.join()
        stream.stop_stream()
        stream.close()
        p.terminate()

    return adjust_volume, stop  # Return control functions for this sound

# List of sounds to play
sounds = [
    
    {"file_path": "./sounds/Background_Bubbles.wav", "volume_db": -5, "loop": True}
    
  
]

# Start playback and store control functions
sound_controls = []
for sound_config in sounds:
    adjust_volume, stop = play_sound(
        sound_config["file_path"],
        sound_config["volume_db"],
        sound_config["loop"]
    )
    sound_controls.append({"adjust_volume": adjust_volume, "stop": stop})

# Handle user input for dynamic control
try:
    print("Press '+' or '-' to adjust volume for all sounds.")
    print("Press 's' to stop all sounds.")
    while True:
        if keyboard.is_pressed('+'):
            print("Increasing volume...")
            for control in sound_controls:
                control["adjust_volume"](+5)  # Decrease volume by 1 dB
            time.sleep(0.2)  # Prevent rapid-fire keypress handling

        elif keyboard.is_pressed('-'):
            print("Decreasing volume...")
            for control in sound_controls:
                control["adjust_volume"](-5)  # Decrease volume by 1 dB
            time.sleep(0.2)

        elif keyboard.is_pressed('s'):
            print("Stopping all sounds...")
            for control in sound_controls:
                control["stop"]()
            break  # Exit the loop after stopping all sounds

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping playback...")
    for control in sound_controls:
        control["stop"]()
