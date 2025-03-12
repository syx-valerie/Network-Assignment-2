# Connects users to the server to allow sending and recieving of messages

import socket
import threading

host = "127.0.0.1"
port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            print(message)
        except:
            print("Connection closed")
            client.close()
            break

def send_messages():
    while True:
        message = input()
        client.send(message.encode())
    
receive_thread = threading.Thread(target = receive_messages)
receive_thread.start()

send_thread = threading.Thread(target = send_messages)
send_thread.start()
