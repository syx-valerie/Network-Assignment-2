# Manages client connections, messages and group functionalities

import socket
import threading

clients = {}  # Store as username: client
groups = {}  # Stores as group name: usernames

def main():
    host = "0.0.0.0"
    port = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print("Server started...")

    while True:
        try:
            client, address = server.accept()
            
            while True:
                client.send("Enter your username: ".encode("utf-8"))
                username = client.recv(1024).decode("utf-8").strip()
                
                if username in clients:
                    client.send("Username is taken. Try again\n".encode("utf-8"))
                else:
                    clients[username] = client
                    print(f"{username} connected from {address}")
                    client.send("Welcome to the chat!\n".encode("utf-8)"))
                    threading.Thread(target = client_handling, args = (client, username)).start()
                    break
        except Exception as e:
            print(f"Something went wrong... Error accepting new connections: {e}")


# Sends message to all other clients except sender
def broadcast(message, sender = None):
    for client in clients.values():
        if client != sender:
            client.send((message + "\n").encode("utf-8"))

# Handles individual client communication
def client_handling(client, username):
    try:
        while True:
            try:
                message = client.recv(1024).decode("utf-8")
                if not message:
                    client.send("Message cannot be left empty. Please type a valid message.\n".encode("utf-8"))
                    continue
            except socket.error as e:
                print(f"Socket error with {username}: {e}")
                break
            
            # Application commands
            if message.startswith("@quit"):
                try:
                    break
                except Exception as e:
                    print(f"An error has occured disconnecting {username}: {e}")
                    client.send("Error during disconnection.\n".encode("utf-8"))

            elif message.startswith("@names"):
                try:
                    if clients:
                        client.send(f"Connected users: {', '.join(clients.keys())}\n".encode("utf-8"))
                    else:
                        client.send("No users are currently online.\n".encode("utf-8"))
                except Exception as e:
                    print(f"Error fetching active users: {e}")
                    client.send("An error has occured while fetching active users.\n".encode("utf-8"))
            
            elif message.startswith("@username "):
                try:
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        raise ValueError("Message format: @username <message>")
                    recipient, msg = parts[1], parts[2]
                    if recipient in clients:
                        clients[recipient].send(f"[Private] {username}: {msg}\n".encode("utf-8"))
                    else:
                        client.send(f"User {recipient} not found.\n".encode("utf-8"))
                except ValueError as e:
                    client.send(f"Error handling private message from {username}: {e}")
                except Exception as e:
                    print(f"An error has occured handling private message from {username}: {e}")
                    client.send("Unexpected error has occured while sending private message.\n".encode("utf-8"))
            
            elif message.startswith("@group set "):
                try:
                    parts = message.split(" ", 3)
                    if len(parts) < 4:
                        raise ValueError("Message format: @group set <group> <member1>, <member2>, ...")
                    group_name, members = parts[2], parts[3].split(", ")
                    if group_name in groups:
                        raise ValueError(f"Group {group_name} already exists.")
                    else:
                        groups[group_name] = members
                        for member in members:
                            if member in clients:
                                clients[member].send(f"Group {group_name} created with members: {', '.join(members)}\n".encode("utf-8"))
                            else:
                                client.send(f"User {member} not found, unable to notify about group creation.\n".encode("utf-8"))
                except ValueError as e:
                    client.send(f"Unable to set group: {e}\n".encode("utf-8"))
                except Exception as e:
                    print(f"An error has occured creating group by {username}: {e}")
                    client.send("Unexpected error has occured while creating group.\n".encode("utf-8"))
            
            elif message.startswith("@group send "):
                try:
                    parts = message.split(" ", 3)
                    if len(parts) < 4:
                        raise ValueError("Message format: @group send <group> <message>")
                    group_name, msg = parts[2], parts[3]
                    if group_name not in groups:
                                raise KeyError(f"Group {group_name} does not exist.")
                    for member in groups[group_name]:
                        if member in clients:
                            clients[member].send(f"[{group_name}] {username}: {msg}\n".encode("utf-8"))
                        else:
                            client.send("You are not in this group or group does not exist.\n".encode("utf-8"))
                except KeyError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except ValueError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except Exception as e:
                    print(f"Error handling group message from {username}: {e}")
                    client.send("Unexpcted error has occured while sending group message.\n".encode("utf-8"))
            
            elif message.startswith("@group delete "):
                try:
                    parts = message.split(" ", 3)
                    if len(parts) < 3:
                        raise ValueError("Message format: @group delete <group>")
                    group_name = parts[2]
                    if group_name not in groups:
                        raise KeyError(f"Group {group_name} does not exist.")
                    if username not in groups[group_name]:
                        raise PermissionError(f"You are not a member of group {group_name}, you do not have permission to delete it.")
                    del groups[group_name]
                    client.send(f"Group {group_name} has been successfully deleted.\n".encode("utf-8"))
                except KeyError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except PermissionError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except ValueError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except Exception as e:
                    print(f"An error has occured handling group deletion by {username}: {e}")
                    client.send("Unexpected error has occured while deleting group.\n".encode("utf-8"))
                    
            elif message.startswith("@group leave "):
                try:
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        raise ValueError("Message format: @group leave <group>")
                    group_name = parts[2]
                    if group_name not in groups:
                        raise KeyError(f"Group {group_name} does not exist.")
                    if username not in groups[group_name]:
                        raise ValueError(f"You are not a member of group {group_name}.")
                    groups[group_name].remove(username)
                    client.send(f"You have left the group {group_name}.\n".encode("utf-8"))
                    if not groups[group_name]:
                        del groups[group_name]  # Deletes group if there are no members left
                except KeyError as e:
                    client.send(f"Error: {e}/n".ecnode("utf-8"))
                except ValueError as e:
                    client.send(f"Error: {e}\n".encode("utf-8"))
                except Exception as e:
                    print(f"Error handling group leave from {username}")
                    client.send("An unexepected error has occured while leaving group.\n".encode("utf-8"))
            
            elif message.startswith("@"):
                client.send(f"Error: '{message}' is an invalid command.\n".encode("utf-8"))
                
            else:
                broadcast(f"{username}: {message}", client)
        
    except Exception as e:
        print(f"Error handling client {username}: {e}")
    finally:
        client.close()
        del clients[username]
        print(f"{username} has disconnected.")
        broadcast(f"{username} has left the chat.")

if __name__ == "__main__":
    main()