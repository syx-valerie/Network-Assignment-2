# Connects users to the server to allow sending and recieving of messages

import socket
import threading

host = "127.0.0.1"
port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((host, port))
except ConnectionRefusedError:
    print("Error: unable to connect to server. Ensure server is running")
    exit()

stop_event = threading.Event()

# Username entry
while True:
    try:
        username_prompt = client.recv(1024).decode()
        if not username_prompt:
            print("Server closed the connection")
            client.close()
            exit()
        print(username_prompt, end = "")
        username = input()
        client.send(username.encode())

        response = client.recv(1024).decode()
        if "Username taken" not in response:
            break
        print(response.strip())
    except (ConnectionResetError, ConnectionAbortedError):
        print("Error: server connection lost")
        client.close()
        exit()

def receive_messages():
    while not stop_event.is_set():
        try:
            message = client.recv(1024).decode()
            if not message:
                print("Server disconnected")
                stop_event.set()
                client.close()
                break
            print(message)
        except ConnectionResetError:
            print("Error: Server connection lost")
            stop_event.set()
            client.close()
            break
        except OSError:
            break

def send_messages():
    while not stop_event.is_set():
        try:
            message = input()
            if message.lower() == '@quit':
                client.send("@quit".encode())
                stop_event.set()
                client.close()
                break
            client.send(message.encode())
        except(BrokenPipeError, ConnectionResetError):
            print("Error: Server connection lost")
            stop_event.set()
            client.close()
            break

# daemon = type of background threads that automatically exit when program terminates
# prevent hanging process, automated cleanup
receive_thread = threading.Thread(target = receive_messages, daemon = True)
send_thread = threading.Thread(target = send_messages, daemon = True)

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()