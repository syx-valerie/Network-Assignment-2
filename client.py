# Connects users to the server to allow sending and recieving of messages

import socket
import threading
import sys

def main():
    host = "127.0.0.1"
    port = 12345

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    username = input(client.recv(1024).decode("utf-8"))
    client.send(username.encode("utf-8"))
    
    threading.Thread(target = receive_messages, args = (client, ), daemon = True).start()

    while True:
        try:
            msg = input("> ")
            if msg == "@quit":
                client.send(msg.encode("utf-8"))
                print("Disconnecting...")
                break
            client.send(msg.encode("utf-8"))
        except KeyboardInterrupt:
            client.send("@quit".encode("utf-8"))
            break

    client.close()
    sys.exit()

def receive_messages(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except Exception as e:
            print(f"Error receiving messages: {e}")
            break

if __name__ == "__main__":
    main()