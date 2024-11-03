import socket
import json
import threading
import time

# Global variable to store the current game state
current_game_state = None

def listen_for_updates():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server and listening for updates...")

        while True:
            try:
                data = s.recv(1024)
                if not data:
                    break
                # Process the incoming data (updates from the server)
                global current_game_state
                current_game_state = json.loads(data.decode('utf-8'))
                print("Received update:", current_game_state)
            except Exception as e:
                print("Error receiving data:", e)
                break

def get_game_state():
    global current_game_state
    # This function can return the latest game state as stored in current_game_state
    return current_game_state

def start_periodic_fetch():
    # Call get_game_state periodically, every second for example
    while True:
        state = get_game_state()
        print("Fetched game state:", state)
        time.sleep(1)

# Start the listening thread to maintain a connection with the server
listener_thread = threading.Thread(target=listen_for_updates)
listener_thread.start()

# Start a separate thread to fetch the game state periodically
fetch_thread = threading.Thread(target=start_periodic_fetch)
fetch_thread.start()
