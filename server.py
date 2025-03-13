# Manages client connections, messages and group functionalities

import socket
import threading

host = "127.0.0.1"
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = {}  # Store client sockets as keys, usernames as values
usernames = {}  # Store username as keys, client sockets as values

# Sends message to all other clients except sender
def broadcast(message, sender = None):
    message = message.encode()
    for client in list(clients.keys()):
        if client != sender:
            try:
                client.send(message)
            except:
                client.close()
                if client in clients:
                    username = clients.pop(client)
                    del usernames[username]

# Handles individual client communication
def client_handling(client):
    try:
        while True:
            client.send("Enter your username: ".encode())
            username = client.recv(1024).decode().strip()

            if username in usernames:
                client.send("Username taken. Please try another.\n".encode())
            else:
                clients[client] = username
                usernames[username] = client
                print(f"{username} has joined the chat")
                broadcast(f"{username} has joined the chat!", sender = client)
                client.send("You have joined the chat.\n".encode())
                break

        while True:
                message = client.recv(1024).decode()
                if not message:
                    break
                broadcast(f"{clients[client]}: {message}")
    except:
            pass
    
    # Handle client disconnection
    if client in clients:
        username = clients.pop(client)
        del usernames[username]
        broadcast(f"{username} has left the chat")
        print(f"{username} disconnected")
    client.close()

def start_server():
    print(f"Server started on {host}:{port}")
    while True:
        client, address = server.accept()
        print(f"New conenction from {address}")
        thread = threading.Thread(target = client_handling, args = (client,))
        thread.start()

start_server()