# Manages client connections, messages and group functionalities

import socket
import threading

host = "127.0.0.1"
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
usernames = {}

# Sends message to all other clients except sender
def broadcast(message, sender = None):
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:
                clients.remove(client)

# Handles individual client communication
def client_handling(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            print(f"Received: {message.decode()}")  # To display message
            broadcast(message, sender = client)
        except:
            clients.remove(client)  # Client disconnected / Removed due to error
            client.close()
            break

def start_server():
    print(f"Server started on {host}:{port}")
    while True:
        client, address = server.accept()
        print(f"New conenction from {address}")
        clients.append(client)
        thread = threading.Thread(target = client_handling, args = (client,))
        thread.start()

start_server()