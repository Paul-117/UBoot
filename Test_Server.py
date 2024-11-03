import json
import socket
import threading
import time

# Dictionary to store connected clients by ID
connected_clients = {}

def handle_client(conn, addr, controler):
    global connected_clients
    client_id = None

    try:
        # Initial setup to receive the client ID
        data = conn.recv(1024)
        if data:
            # Assume the client sends their ID as the first message
            command = json.loads(data.decode('utf-8'))
            if "ID" in command:
                client_id = command["ID"]
                connected_clients[client_id] = conn
                print(f"Client '{client_id}' connected from {addr}")

        while True:
            data = conn.recv(1024)
            if not data:
                break

            # Decode received data
            command = json.loads(data.decode('utf-8'))

            # Check the client ID and process requests accordingly
            if client_id == "Console" and command["type"] == "get":
                # Send the initial game state to the Console client
                game_state = controler.get_game_state() if hasattr(controler, 'get_game_state') else 5
                conn.sendall(json.dumps(game_state).encode('utf-8'))
                
            elif client_id == "Console" and command["type"] == "update":
                # Handle game state update if requested by Console
                controler.update_game_state(command["data"]) if hasattr(controler, 'update_game_state') else None
                print("Game state updated by Console")

    finally:
        # Remove client from the dictionary upon disconnection
        if client_id in connected_clients:
            del connected_clients[client_id]
        conn.close()
        print(f"Client '{client_id}' disconnected")

def send_update_to_client(client_id, update_data):
    global connected_clients
    if client_id in connected_clients:
        client_conn = connected_clients[client_id]
        update_message = json.dumps({"type": "update", "data": update_data}).encode('utf-8')
        try:
            client_conn.sendall(update_message)
            print(f"Sent update to '{client_id}': {update_data}")
        except Exception as e:
            print(f"Failed to send update to '{client_id}':", e)
            # Remove the client if sending fails
            del connected_clients[client_id]

def server_program(controler):
    HOST = "0.0.0.0"
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            # Start a new thread for each client
            threading.Thread(target=handle_client, args=(conn, addr, controler)).start()

def periodic_update(controler):
    # Example of selectively sending an update
    while True:
        # Check for updates or generate an update condition
        update_data = controler.get_updated_state() if hasattr(controler, 'get_updated_state') else {"state": "periodic_update"}
        
        # Send update to a specific client (e.g., "Console")
        send_update_to_client("Console", update_data)
        time.sleep(5)  # Update interval

# Example mock controler with basic functionality for testing
class MockControler:
    def get_game_state(self):
        return {"state": "initial_game_state"}

    def get_updated_state(self):
        return {"state": "updated_game_state"}

    def update_game_state(self, new_state):
        print("Updating game state with:", new_state)

# Start the server and periodic update threads
controler = MockControler()
server_thread = threading.Thread(target=server_program, args=(controler,))
server_thread.start()

update_thread = threading.Thread(target=periodic_update, args=(controler,))
update_thread.start()
