import socket
import json
import threading
import time

def listen_for_messages(s):
    """Thread function to continuously listen for messages from the server."""
    try:
        while True:
            # Receiving messages from the server
            data = s.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            # Decode and print the message from the server
            message = json.loads(data.decode('utf-8'))
            print("Message from server:", message)
    except Exception as e:
        print("Error receiving data:", e)
    finally:
        s.close()

def client_program():
    HOST = "127.0.0.1"  # Server's IP address
    PORT = 8080

    # Set up a persistent connection with the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("Connected to server")

            # Start a separate thread to listen for incoming messages
            threading.Thread(target=listen_for_messages, args=(s,)).start()

            # Main loop to send commands to the server
            while True:
                # Example of sending a 'get' command to retrieve the game state
                command_type = input("Enter command type ('get' or 'update'): ")
                if command_type == "get":
                    command = json.dumps({"type": "get", "ID": "Voltarium"}).encode('utf-8')
                    s.sendall(command)
                elif command_type == "update":
                    # Example 'new_state' to send
                    new_state = {"score": 100, "level": 2}
                    command = json.dumps({"type": "update", "ID": "Voltarium", "data": new_state}).encode('utf-8')
                    s.sendall(command)
                else:
                    print("Invalid command. Please enter 'get' or 'update'.")

                # Small delay to avoid flooding the server with requests
                time.sleep(0.5)

        except Exception as e:
            print("Error connecting to the server:", e)

# Run the client program
client_program()
