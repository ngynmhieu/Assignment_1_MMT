import socket
import threading

# Constants
IP = socket.gethostbyname(socket.gethostname())
PORT = 60000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

# Global Variables
file_info = {}
client_sockets = {}
event_flag = threading.Event()

def add_file_info(filename, hostname, last_modified, file_size):
    """Adds or updates file information in the database."""
    client_info = {"hostname": hostname, "last_modified": last_modified, "file_size": file_size}
    
    # Initialize the list for the filename if not already present
    if filename not in file_info:
        file_info[filename] = []

    # Check for existing entry for the same hostname
    existing_entries = file_info[filename]
    for existing_info in existing_entries:
        if existing_info['hostname'] == hostname:
            existing_info.update(client_info)
            break
    else:
        # Append new client info if the hostname is not already present
        file_info[filename].append(client_info)

def add_files_from_a_client(client_file_info, hostname):
    """Processes and adds multiple files information from a client."""
    for line in client_file_info.strip().split('\n'):
        filename, last_modified, file_size = line.split('|')
        add_file_info(filename, hostname, last_modified, file_size)

def remove_client_from_a_file(filename, hostname_to_remove):
    """Removes a client's information from a specific file."""
    if filename in file_info:
        file_info[filename] = [client for client in file_info[filename] if client['hostname'] != hostname_to_remove]
        if not file_info[filename]:
            del file_info[filename]

def get_file_info(filename):
    """Retrieves file information."""
    return file_info.get(filename, None)

def remove_hostname_from_file_info(hostname):
    """Removes a hostname and its associated information from the database."""
    for filename in list(file_info.keys()):
        remove_client_from_a_file(filename, hostname)
    client_sockets.pop(hostname, None)

def add_client_info(client_socket, hostname, upload_port):
    """Adds client socket information."""
    client_sockets[hostname] = {"socket": client_socket, "upload_port": upload_port}

def get_client_info(hostname):
    """Retrieves client information."""
    return client_sockets.get(hostname, None)

def process_discover_list(client_file_info, hostname, event_flag):
    """Processes the discovered list of files from a client."""
    add_files_from_a_client(client_file_info, hostname)
    print(f"Files from {hostname}:")
    for filename in file_info:
        print(f"{filename} - Last Modified: {file_info[filename]['last_modified']} - Size: {file_info[filename]['file_size']}")

def handle_publish(msg, hostname):
    """Handles the publish command from a client."""
    filename, last_modified, file_size = msg.split("|")
    add_file_info(filename, hostname, last_modified, file_size)

def check_file_status(conn, requesting_client, requested_client, filename):
    """Checks the status of a file from a specific client."""
    client_socket_info = get_client_info(requested_client)
    if client_socket_info:
        client_socket = client_socket_info["socket"]
        client_socket.send(f"CHECK_STATUS@{filename}|{requesting_client}".encode(FORMAT))        
    else:
        conn.send("REPLY_PEER@N/A".encode(FORMAT))

def handle_fetch(filename, conn, requesting_client):
    """Handles the fetch command for a file."""
    per_file_info = get_file_info(filename)
    if per_file_info:
        msg = "REPLY_FETCH@" + "|".join([f"{info['hostname']}|{info['last_modified']}|{info['file_size']}" for info in per_file_info if info['hostname'] != requesting_client])
        conn.send(msg.encode(FORMAT))
    else:
        conn.send("REPLY_PEER@N/A".encode(FORMAT))

def handle_client(conn, addr, event_flag):
    """Manages the interaction with a connected client."""
    try:
        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            if not data:
                break

            cmd, msg = data.split("@", 1)
            process_client_command(cmd, msg, conn, addr)
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        remove_hostname_from_file_info(addr[0])
        conn.close()

def process_client_command(cmd, msg, conn, addr):
    """Processes the command received from the client."""
    command_handlers = {
        "PUBLISH": handle_publish,
        "FETCH": handle_fetch
        # Add more command-key: function-value pairs as needed
    }

    if cmd in command_handlers:
        command_handlers[cmd](msg, conn, addr[0])
    else:
        print(f"Received unknown command '{cmd}' from {addr}")


def get_user_input(event_flag):
    """
    Handles server-side user input for commands like discovering file lists
    and pinging clients.
    """
    while True:
        user_input = input("Enter a command (discover [hostname] / ping [hostname]): ").strip()
        if user_input.lower() == 'exit':
            break

        try:
            cmd, hostname = user_input.split()
        except ValueError:
            print("Invalid command format. Use 'discover [hostname]' or 'ping [hostname]'.")
            continue

        if cmd == "discover":
            event_flag.clear()
            get_hostname_repo(hostname, event_flag)
        elif cmd == "ping":
            event_flag.clear()
            live_check(hostname, event_flag)
        else:
            print("Unknown command. Use 'discover [hostname]' or 'ping [hostname]'.")

        event_flag.wait()  # Wait for the operation to complete

def get_hostname_repo(hostname, event_flag):
    """
    Retrieves repository information for a specific hostname.
    """
    client_info = get_client_info(hostname)
    if client_info:
        client_info['socket'].send("DISCOVER@".encode(FORMAT))
    else:
        print(f"Client {hostname} does not exist or has disconnected.")
        event_flag.set()

def live_check(hostname, event_flag):
    """
    Performs a live check for a specific hostname.
    """
    client_info = get_client_info(hostname)
    if client_info:
        client_info['socket'].send("PING@".encode(FORMAT))
    else:
        print(f"Client {hostname} does not exist or has disconnected.")
        event_flag.set()

def start_server():
    """Initializes and starts the server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server listening on {IP}:{PORT}")

    cli = threading.Thread(target=get_user_input, args=(event_flag,))
    cli.start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, event_flag))
        thread.start()

if __name__ == "__main__":
    start_server()
