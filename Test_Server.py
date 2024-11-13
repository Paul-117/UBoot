import json
import socket
import threading

class Display:
    """Class responsible for analyzing and displaying messages from clients."""
    def __init__(self):
        print("Server Display initialized")

    def show_message(self, addr, message):
        """Displays the received message along with client address."""
        print(f"Message from {addr}: {message}")

class Server:
    """Class to handle server functions including client connections, receiving and sending messages."""
    def __init__(self, host, port, display):
        self.host = host
        self.port = port
        self.display = display
        self.connected_clients = []  # Stores (conn, addr) tuples

        # Start the server and listen for clients
        self.start_server()

    def start_server(self):
        """Sets up the server to accept incoming connections."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print("Server is listening...")

        # Start a thread to accept client connections
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """Accept new clients and start a handler thread for each client."""
        while True:
            conn, addr = self.socket.accept()
            self.connected_clients.append((conn, addr))
            print(f"Client connected from {addr}")

            # Start a new thread to handle each client’s messages
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        """Handles communication with a connected client."""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"Client {addr} disconnected.")
                    break

                # Decode and display the message from the client
                command = json.loads(data.decode('utf-8'))
                self.display.show_message(addr, command)


        except ConnectionResetError:
            print(f"Connection with {addr} was reset.")
        finally:
            # Clean up on disconnection
            self.connected_clients.remove((conn, addr))
            conn.close()

    def send_message_to_client(self, addr, message):
        """Send a custom message to a specific client by address."""
        # Find the connection for the given address
        for conn, client_addr in self.connected_clients:
            if client_addr == addr:
                try:
                    response = json.dumps(message).encode('utf-8')
                    conn.sendall(response)
                    print(f"Sent message to {addr}: {message}")
                except BrokenPipeError:
                    print(f"Connection with {addr} lost while sending message.")
                break
        else:
            print(f"Client {addr} not found.")

    def broadcast_message(self, message):
        """Send a message to all connected clients."""
        response = json.dumps(message).encode('utf-8')
        for conn, addr in self.connected_clients[:]:
            try:
                conn.sendall(response)
                print(f"Broadcasted message to {addr}: {message}")
            except BrokenPipeError:
                print(f"Connection with {addr} lost while broadcasting message.")
                self.connected_clients.remove((conn, addr))

# Usage example
if __name__ == "__main__":
    # Initialize the display object for the server
    display = Display()
    
    # Create and start the server instance
    server = Server("0.0.0.0", 8080, display)

    # Example of sending a message to a specific client (you can replace with actual client addresses)
    # Here, you'd interactively call this in response to specific events
    # server.send_message_to_client(("127.0.0.1", 12345), "Hello Client!")
    
    # Example of broadcasting a message
    # server.broadcast_message("Hello to all connected clients!")

    # Keep the main thread alive
    while True:
        input("Press Enter to broadcast a message to all clients...\n")
        msg = input("Enter your message: ")
        server.broadcast_message(msg)
