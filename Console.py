import tkinter as tk
from tkinter import ttk
import pickle
import socket
import json
import threading
import time
from Bridge import Player


class Client:
    """Class to handle client connection, message listening, and message sending."""
    def __init__(self, host, port,Console):

        self.Console = Console
        self.host = host
        self.port = port
        
        self.socket = None

        # Connect to the server on initialization
        self.connect_to_server()

        # Start a thread to listen for incoming messages
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()
        

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
                print("Recieved: ", message)
                               
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





class RetroConsole(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Retro Console with Tabs")
        self.configure(bg="black")

        # Initialize position variables
        self.x, self.y = 0, 0  # Your position
        self.others_positions = []  # Positions of others
        self.detected_ships = self.create_ship_data()  # Create ship data

        # Configure custom style for tabs
        style = ttk.Style(self)
        style.theme_use("default")  # Use default theme for custom modifications
        style.configure("TNotebook", background="black", borderwidth=0)
        style.configure("TNotebook.Tab", background="black", foreground="green",
                        padding=[10, 5], font=("Courier", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "black")], foreground=[("selected", "light green")])
        
        # Set up the notebook for tabs
        notebook_frame = tk.Frame(self, bg="green", bd=2)
        notebook_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(padx=2, pady=2, fill="both", expand=True)

        # Initialize tabs
        self.Story_tab = self.create_tab("Story")
        self.Located_Ships_tab = self.create_tab("Located Ships")
        self.Test_tab = self.create_tab("Test")

        # Set default tab
        self.notebook.select(self.Story_tab)
        
        # Key bindings for tab switching
        self.bind("s", lambda event: self.show_tab("Story"))
        self.bind("l", lambda event: self.show_tab("Located Ships"))
        self.bind("t", lambda event: self.show_tab("Test"))

        # Display initial info
        self.update_Story_tab("Lore.txt", delay=0.1)  # Ensure delay is a float
        self.update_Located_Ships_tab()
        self.update_test_tab()

        # Set a recurring task to update positions
        self.after(1000, self.update_positions)  # Update positions every second

        # Display typing effect text on Message tab from a file
        
    def create_tab(self, title):
        """Creates a tab with a retro-styled Text widget."""
        frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(frame, text=title)
        
        text_widget = tk.Text(frame, bg="black", fg="green", insertbackground="green",
                              font=("Courier", 12), height=20, width=50, wrap="word")
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("end", f"--- {title} Tab ---\n")
        text_widget.config(state="disabled")  # Make read-only
        
        setattr(self, f"{title.lower()}_text", text_widget)  # Dynamic attribute for text widget
        return frame

    def show_tab(self, title):
        """Switches to the specified tab by title."""
        if title == "Story":
            self.notebook.select(self.Story_tab)
        elif title == "Located Ships":
            self.notebook.select(self.Located_Ships_tab)
        elif title == "Test":
            self.notebook.select(self.Test_tab)


    def create_ship_data(self):
        """Creates a list of dictionaries containing ship data."""
        return [
            {
                "class": "Destroyer",
                "arsenal": "Torpedoes, Guns",
                "health": "80%",
                "max_speed": "30 knots",
                "agility": "High",
                "last_known_position": "45.0N, 25.0W",
                "course": "Northeast",
            },
            {
                "class": "Cruiser",
                "arsenal": "Missiles, CIWS",
                "health": "70%",
                "max_speed": "28 knots",
                "agility": "Medium",
                "last_known_position": "44.0N, 26.0W",
                "course": "East",
            },
            {
                "class": "Battleship",
                "arsenal": "Heavy Guns, Missiles",
                "health": "60%",
                "max_speed": "25 knots",
                "agility": "Low",
                "last_known_position": "43.0N, 27.0W",
                "course": "Southeast",
            },
            {
                "class": "Submarine",
                "arsenal": "Torpedoes",
                "health": "90%",
                "max_speed": "20 knots",
                "agility": "Very High",
                "last_known_position": "46.0N, 24.0W",
                "course": "West",
            },
        ]

    def update_Located_Ships_tab(self):
        
        # Update text widget
        others_text = getattr(self, "located ships_text")
        others_text.config(state="normal")
        others_text.delete(1.0, "end")  # Clear previous text
        others_text.insert("end", "--- Detected Ships ---\n")
        
        
        # Display each ship's information
        for i, ship in enumerate(self.detected_ships, start=1):
            others_text.insert("end", f"Ship {i}:\n")
            others_text.insert("end", f"  Class: {ship['class']}\n")
            others_text.insert("end", f"  Arsenal: {ship['arsenal']}\n")
            others_text.insert("end", f"  Health: {ship['health']}\n")
            others_text.insert("end", f"  Max Speed: {ship['max_speed']}\n")
            others_text.insert("end", f"  Agility: {ship['agility']}\n")
            others_text.insert("end", f"  Last Known Position: {ship['last_known_position']}\n")
            others_text.insert("end", f"  Course: {ship['course']}\n")
            others_text.insert("end", "------------------------\n")
        
        others_text.config(state="disabled")  # Make read-only

    def update_Story_tab(self, filepath, delay=0.1):
        """Types text from a file one letter at a time on the Message tab."""
        message_text = getattr(self, "story_text")
        message_text.config(state="normal")  # Enable writing

        # Clear previous text
        message_text.delete(1.0, "end")
        message_text.insert("end", "--- Message Tab ---\n")

        # Open the file and read text
        with open(filepath, "r") as file:
            self.text_to_type = file.read()  # Store text to type out
        self.current_char_index = 0  # Initialize character index

        # Start the typing effect using after instead of time.sleep
        self._type_next_char(message_text, int(delay * 1000))  # Convert delay to milliseconds

    def _type_next_char(self, message_text, delay):
        """Helper function to insert the next character in the message."""
        if self.current_char_index < len(self.text_to_type):
            char = self.text_to_type[self.current_char_index]
            message_text.insert("end", char)
            message_text.see("end")  # Scroll to end
            self.current_char_index += 1
            self.after(delay, lambda: self._type_next_char(message_text, delay))
        else:
            message_text.config(state="disabled")  # Make read-only once done

    def update_test_tab(self):
        """Updates the Test tab."""
        # Update text widget
        test_text = getattr(self, "test_text")
        test_text.config(state="normal")
        test_text.delete(1.0, "end")  # Clear previous text

        test_text.insert("end", "--- Test Tab ---\n")
        test_text.insert("end", "This is a test message.\n")
        
        test_text.config(state="disabled")  # Make read-only



#Display = RetroConsole()
Console = 5
client = Client("127.0.0.1", 8080, Console)

#Display.mainloop()

def ini():
    
    client.send({"ID": "Console", "request": "Initialize"})
    time.sleep(3)
    client.send({"ID": "Console", "request": "get"})

ini()

i = 0
while True:
    i +=1 
    print(i)
    time.sleep(1)
    
