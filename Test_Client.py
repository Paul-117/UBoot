import socket
import json
import threading
import time

class Display:
    """Class responsible for analyzing and displaying messages from the server."""
    def __init__(self):
        print("Display initialized")

    def show_message(self, message):
        """Analyzes and displays the received message."""
        print("Displaying message:", message)
        # Implement further analysis or formatting of message as needed


class Client:
    """Class to handle client connection, message listening, and message sending."""
    def __init__(self, host, port, display):
        self.host = host
        self.port = port
        self.display = display
        self.socket = None

        # Connect to the server on initialization
        self.connect_to_server()

        # Start a thread to listen for incoming messages
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()
        self.send("Console")

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
                self.display.show_message(message)
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

# Usage example
if __name__ == "__main__":
    # Initialize the display object
    display = Display()
    
    # Initialize the client with server details and the display instance
    client = Client("127.0.0.1", 8080, display)

