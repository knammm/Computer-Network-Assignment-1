import socket
# import time
import threading
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

BYTES = 102400


class tracking_server:
    def __init__(self):
        # Init socket properties
        self.host = self.get_local_ip()
        self.port = 18520

        # Init log
        self.log = []  # List of string
        self.log.append(f'[System Anouncement] Host is running at {self.host}, port {self.port}')

        # Init socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))  # Tuple of (IP, Port)
        # self.server_socket.settimeout(5)
        self.server_socket.listen()
        self.log.append(f'[System Anouncement] Server is running !')

        # Init other properties
        self.client_servers = {}  # Key: peerIP - Value: port
        self.file_client = {}  # Key: fileName - Value: list of peers
        self.counter = 0

    def get_local_ip(self):
        try:
            # Create a socket object and connect to an external server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))  # Google's public DNS server and port 80
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error:
            return "Unable to determine local IP"

    def get_log(self):
        return self.log

    def get_clients(self):
        return self.client_servers

    def get_available_files(self, address):
        # Function return a list of Files are available for the client address
        fileList = []
        for file in self.file_client.keys():
            if address in self.file_client[file]:
                fileList.append(file)

        return fileList

    def handle_clients(self, connection, address):
        print(f'[System Anouncement] Accept new connection from {address[0]} !')
        self.log.append(f'[System Anouncement] Accept new connection from {address[0]} !')
        welcome_message = "[Announcement]--Welcome to P2P File Sharing application !--".encode("utf-8")
        connection.send(welcome_message)

        # Receive IP and port from client
        init_message = connection.recv(BYTES).decode("utf-8")
        clientIP = address[0]
        clientPort = int(init_message)  # send the FILE_PORT
        self.client_servers[clientIP] = clientPort

        print(self.client_servers)

        while True:
            recv_message = connection.recv(BYTES).decode("utf-8")
            if recv_message != "":
                frag_message = recv_message.split(" ")
                client_cmd = frag_message[0]
                print(f"Receive: {recv_message}")
            else:
                frag_message = ""
                client_cmd = ""
            if client_cmd == 'Download':
                # Client sent 'Download'
                magnet_text = int(frag_message[1])
                if magnet_text in self.file_client:
                    # Process peers dictionary
                    print(f"Hello: {self.file_client}")
                    print(f"Client_Port: {self.client_servers}")
                    peers_info = {}
                    clients_ip = self.file_client[magnet_text]
                    ports = []
                    for client in clients_ip:
                        ports.append(self.client_servers[client])

                    # peers_info['id'] = f"{clientIP}:{clientPort}"
                    peers_info['ip'] = clients_ip
                    peers_info['port'] = ports

                    send_data = f"[Anouncement]--Download Successfully--{magnet_text}--"  # Split by --
                    send_data += f"{peers_info}"

                    self.file_client[magnet_text].append(clientIP)  # Append new IP
                else:
                    send_data = f"[Failure]--Download Failed--No File Found--"

                self.log.append(f"[System Anouncement] {clientIP}: Download")
                connection.send(send_data.encode("utf-8"))

            elif client_cmd == 'Upload':
                # Send a unique ID
                print("Upload successfully")
                send_data = f"[Announcement]--Upload Successfully--{self.counter}"
                self.file_client[self.counter] = []
                self.file_client[self.counter].append(clientIP)
                self.counter += 1
                self.log.append(f"[System Anouncement] {clientIP}: Upload")
                connection.send(send_data.encode("utf-8"))

            elif client_cmd == 'Disconnect':
                # Client sent 'Disconnect'
                self.client_servers.pop(clientIP)
                file_list = self.get_available_files(clientIP)
                for file in file_list:
                    # Remove the clientIP out of the file_client
                    self.file_client[file].remove(clientIP)
                    if self.file_client[file].count() == 0:
                        # Case: no client has this file
                        self.file_client.pop(file)

                self.log.append(f"[System Anouncement] {clientIP}: Disconnect")
                send_data = "[Disconnect]--Success--".encode("utf-8")
                connection.send(send_data)
                break

            elif client_cmd == 'Waiting':
                # Client did not send any massage -> refers to '\0'
                send_data = f'[Announcement]--Waiting--'.encode("utf-8")
                connection.send(send_data)

            else:
                send_message = f'[Failure]--Invalid Format--'.encode("utf-8")
                connection.send(send_message)

    def start_server(self):
        while True:
            try:
                clientSocket, clientAddress = self.server_socket.accept()
                clientCommand = threading.Thread(target=self.handle_clients(clientSocket, clientAddress))
                clientCommand.start()
            except:
                pass


if __name__ == "__main__":
    server = tracking_server()
    server.start_server()
    # magnet_text = "alice"
    # server.file_client[magnet_text] = ["1.1.1.1", "10.1.1.1"]
    # server.client_servers = {"1.1.1.1": 9090, "10.1.1.1": 2000, "2.1.41.2": 6969}
    # magnet_text_test = "alice"
    # send_data = ""
    # if magnet_text_test in server.file_client:
    #     # Process peers dictionary
    #     peers_info = {}
    #     clients_ip = server.file_client[magnet_text_test]
    #     ports = []

    #     for client in clients_ip:
    #         ports.append(server.client_servers[client])

    #     # peers_info['id'] = f"{clientIP}:{clientPort}"
    #     peers_info['ip'] = clients_ip
    #     peers_info['port'] = ports

    #     send_data = "[Anouncement]--Download Successfully--"  # Split by --
    #     send_data += f"{peers_info}"

    #     server.file_client[magnet_text_test].append('9.9.9.9')
    #     print(send_data)

    # split_data = send_data.split("--")

    # announcement = split_data[0]
    # success_message = split_data[1]
    # peer_info = eval(split_data[2])  # Use eval to convert the string representation of dictionary back to dictionary

    # print(announcement)
    # print(success_message)
    # print(peer_info)

    # print("=======")
    # peer_info['ip'].remove("1.1.1.1")
    # print(peer_info)
