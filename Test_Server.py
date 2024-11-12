import json
import socket
import threading
import time

connected_clients = []

def handle_client(conn, addr):

    global connected_clients

    connected_clients.append(conn)
    print("cliend connected:", conn, addr)
    print("New communication thread started")

    try:
        while True:
            data = conn.recv(1024)
            
            if not data:
                print("break")
                break
            print("data recieved: ", data )
            # Decode received data
            command = json.loads(data.decode('utf-8'))
            print("recieved:", command)
            back = "Message recieved"
            response = json.dumps(back).encode('utf-8')

            
            conn.sendall(response)

    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    
def server_program():
    HOST = "0.0.0.0"
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()



server_program()


import json
import socket
import threading

connected_clients = []

def handle_client(conn, addr):
    global connected_clients

    connected_clients.append(conn)
    print(f"Client connected: {addr}")
    print("New communication thread started")

    # Start a separate thread to send messages to the client
    threading.Thread(target=send_messages, args=(conn,)).start()

    try:
        while True:
            # Receive messages from the client
            data = conn.recv(1024)
            if not data:
                print("Client disconnected")
                break
            
            print("Data received:", data)
            
            # Decode received data
            command = json.loads(data.decode('utf-8'))
            print("Received:", command)
            
            # Send automatic acknowledgment response back to the client
            response = json.dumps("Message received").encode('utf-8')
            conn.sendall(response)

    except ConnectionResetError:
        print(f"Connection with {addr} was reset.")
    finally:
        conn.close()
        connected_clients.remove(conn)

def send_messages(conn):
    try:
        while True:
            # Wait for Enter press to send a message
            input("Press Enter to send a message to the client...")
            message = input("Enter your message: ")
            response = json.dumps(message).encode('utf-8')
            conn.sendall(response)
            print("Sent message to client:", message)
    except BrokenPipeError:
        print("Connection lost while trying to send a message.")
    finally:
        conn.close()

def server_program():
    HOST = "0.0.0.0"
    PORT = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

# Run the server program
server_program()
