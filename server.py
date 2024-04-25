import socket
# import time
import threading

BYTES = 102400
class tracking_server:
    def __init__(self):
        # Init socket properties
        self.host = self.get_local_ip()
        self.port = 12345

        # Init log
        self.log = []  # List of string
        self.log.append(f'[System Anouncement] Host is running at {self.host}, port {self.port}')

        # Init socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))  # Tuple of (IP, Port)
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
        self.log.append(f'[System Anouncement] Accept new connection from {address} !')
        welcome_message = "[Announcement]--Welcome to P2P File Sharing application !--".encode("utf-8")
        connection.send(welcome_message)

        # Receive IP and port from client
        init_message = connection.recv(BYTES).decode("utf-8")
        clientIP = address
        clientPort = init_message # send the FILE_PORT
        self.client_servers[clientIP] = clientPort

        while True:
            recv_message = connection.recv(BYTES).decode("utf-8")
            recv_message.split(" ")
            client_cmd = recv_message[0]

            if client_cmd == 'Download':
                # Client sent 'Download'
                magnet_text = recv_message[1]
                if magnet_text in self.file_client:
                    # Process peers dictionary
                    peers_info = {}
                    clients_ip = self.file_client[magnet_text]
                    ports = []
                    for client in clients_ip:
                        ports = ports.append(self.client_servers[client])

                    # peers_info['id'] = f"{clientIP}:{clientPort}"
                    peers_info['ip'] = clients_ip
                    peers_info['port'] = ports

                    send_data = "[Anouncement]--Download Successfully--"  # Split by --
                    send_data += f"{peers_info}"

                    self.file_client[magnet_text].append(clientIP)  # Append new IP
                else:
                    send_data = "[Failure]--Download Failed--No File Found"

                self.log.append(f"[System Anouncement] {clientIP}: Download")
                connection.send(send_data.encode("utf-8"))

            elif client_cmd == 'Upload':
                # Send a unique ID
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
                send_data = "[Warning]--Waiting--".encode("utf-8")
                connection.send_data(send_data)

            else:
                send_message = f'[Failure]--Invalid Format--'.encode("utf-8")
                connection.send(send_message)

    def start_server(self):
        while True:
            try:
                print(self.log)
                clientSocket, clientAddress = self.server_socket.accept()
                clientCommand = threading.Thread(target=self.handle_clients, arg=(clientSocket, clientAddress))
                clientCommand.start()
            except:
                pass

class MainApplication(tk.Tk):
    def __init__(self) -> None:
        # Initialize the main application window
        tk.Tk.__init__(self)
        print("Initializing MainViewSettingsTab")

        s = ttk.Style()
        s.theme_use("clam")

        self.title("Simple file-sharing application")
        self.geometry("800x460")

        self.main_view = MainView(self)
        self.main_view.pack()

class MainView(ttk.Frame):
    def __init__(self, parent):
        # Initialize the main view frame
        super().__init__(parent)
        self.parent = parent
        self.server = tracking_server()

        self.create_widgets()

        start_server = threading.Thread(target=self.server.start_server, args=())
        start_server.start()

    def create_widgets(self):
        # Create widgets for the main view
        self.tab_control = ttk.Notebook(self)

        self.home_tab = HomeTab(self)
        self.tab_control.add(self.home_tab, text="Home")

        self.log_tab = LogTab(self)
        self.tab_control.add(self.log_tab, text="Statistics")

        self.tab_control.pack(expand=1, fill="both")

class HomeTab(ttk.Frame):
    def __init__(self, parent):
        # Initialize the Home tab frame
        super().__init__(parent)
        self.parent = parent
        #self.style = ttk.Style()  # Initialize style here
        self.create_widgets()

    def create_widgets(self) -> None:
        # Create widgets for the Home tab
        print("Creating widgets for MainViewFilesTab")

        # Create a frame for the files tree with a light gray background and padding
        self.files_frame = ttk.Frame(self, padding=10, style="FilesFrame.TFrame")

        # Create the files tree
        self.files_tree = ttk.Treeview(self.files_frame)

        # Define tree columns
        self.files_tree["columns"] = (
            "Client",
            "status",
        )

        # Format columns
        self.files_tree.column("#0", width=0, stretch=tk.NO)
        self.files_tree.column("Client", anchor=tk.CENTER, width=225)
        self.files_tree.column("status", anchor=tk.CENTER, width=75)

        # Create headings
        self.files_tree.heading("#0", text="", anchor=tk.W)
        self.files_tree.heading("Client", text=" List of Clients", anchor=tk.CENTER)
        self.files_tree.heading("status", text=" Status", anchor=tk.CENTER)


        self.files_tree.pack(expand=1, fill="both")

        # Pack the files frame with a light gray background and border
        self.files_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Add Label to display tracking server IP address
        self.ip_label = ttk.Label(self, text="Tracking Server IP: " + self.parent.server.get_local_ip(), style="IPLabel.TLabel", font=("Times New Roman", 13,"bold"))
        self.ip_label.pack(side=tk.BOTTOM, pady=5)

        # Add Label and Entry for IP address
        self.ip_address_label = ttk.Label(self, text="Enter IP address:", font=("Times New Roman", 14))
        self.ip_address_entry = ttk.Entry(self, width=50)

        self.ip_address_label.pack(side=tk.LEFT, padx=(10, 5))
        self.ip_address_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.ip_address_entry.bind("<Key>", self.update_font)

        # Add Search button with custom style and light blue background
        self.discover_button = ttk.Button(
            self,
            text="Search",
            command=self.discover,
            style="Custom.TButton",
        )
        self.discover_button.pack(side=tk.LEFT, padx=(5,5), pady=(5, 4))

        # Add Reset button with custom style and light green background
        self.refresh_button = ttk.Button(
            self,
            text="Reset",
            command=self.ping,
            style="Custom.TButton",
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(5, 5), pady=(5, 4))

        # Define custom styles for the buttons with background colors and border
        self.style = ttk.Style()
        # self.style.configure("Custom.TButton",
        #                      # background="#ADD8E6",  # Light blue background color for Discover button
        #                      foreground="black",
        #                      padding=10,
        #                      font=('Times New Roman', 14, 'bold'))

        # Define custom style for the files frame with a light gray background and border
        self.style.configure("FilesFrame.TFrame",
                             background="blue",  # Light gray background color
                             borderwidth=2,
                             relief="raised")

        # Define custom style for the IP address label
        self.style.configure("IPLabel.TLabel",
                             background="#FFFFFF",  # White background color
                             foreground="#000000",  # Black text color
                             font=('Times New Roman', 14, 'bold'))

        self.style.configure("Treeview.Heading", font=("Times New Roman", 13, "bold"), foreground="black", background="yellow")
        ####################################################MODIFY#######################
        #self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.TButton",
                             foreground="white",
                             background="#2196F3",  # Green
                             borderwidth=0,
                             font=("Times New Roman", 14, "bold"),
                             padding=10)
        self.style.map("Custom.TButton",
                       background=[("active", "#6E8B9D")])  # Darker green when active

    def update_font(self, event):
        self.ip_address_entry.configure(font=("Times New Roman", 11)) #Enter IP's address

    def ping(self):
        # Function to refresh file list HOMETAB
        print("Refreshing file list in MainViewFilesTab")
        # Add code to refresh file list
        self.populate_tree()

    def populate_tree(self) -> None:
        # Function to populate file tree
        print("Populating file tree in MainViewFilesTab")
        # Clear existing items in the tree
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)

        self.clients = self.parent.server.get_clients()

        # Insert new file data into the tree
        for i, client_ip in enumerate(self.clients):
            client = f"{client_ip} Active"
            self.files_tree.insert('', tk.END, iid=i, values=client)

    def discover(self):
        # Function to discover files
        # TODO: Show the file of the addr
        client_ip = self.ip_address_entry.get().strip()

        # Validate the IP address
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", client_ip):
            messagebox.showerror("Error", "Invalid IP address")
            return

        # Get file list from the server using the get_available_files method
        files = self.parent.server.get_available_files(client_ip)

        # If no files found
        if not files:
            messagebox.showinfo("Info", f"No files found on client {client_ip}")
            return

        # Create a new window to display files
        files_window = FileListWindow(self, client_ip, files)
        files_window.grab_set()


class FileListWindow(tk.Toplevel):
    def __init__(self, parent, client_ip, files):
        # Initialize the file list window
        super().__init__(parent)
        self.parent = parent
        self.client_ip = client_ip
        self.files = files

        self.title(f"Files on {client_ip}")
        self.geometry("500x300")

        # Create a frame to hold the list
        self.files_frame = ttk.Frame(self)
        self.files_frame.pack(expand=True, fill="both")

        # Create a listbox to show files
        self.files_list = tk.Listbox(self.files_frame)
        for file in files:
            self.files_list.insert(tk.END, file)
        self.files_list.pack(expand=True, fill="both")

        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.close_button.pack(side=tk.RIGHT)


class SaveFileDialog(tk.Toplevel):
    def __init__(self, parent, file_path):
        # Initialize the save file dialog
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.create_widgets()

    def create_widgets(self):
        # Create widgets for the save file dialog
        self.file_path_label = ttk.Label(self, text="File Path:")
        self.file_path_label.grid(row=0, column=0)

        self.file_path_entry = ttk.Entry(self)
        self.file_path_entry.grid(row=0, column=1, padx=6, pady=4)

        self.browse_button = ttk.Button(
            self, text="Browse", command=self.browse_file_path
        )
        self.browse_button.grid(row=0, column=2)

        self.save_button = ttk.Button(
            self, text="Save", command=self.save_file, style="Accent.TButton"
        )
        self.save_button.grid(row=1, column=0, columnspan=3, padx=6, pady=8)

    def browse_file_path(self):
        # Function to browse file path
        file_path = filedialog.asksaveasfilename()
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def save_file(self):
        # Function to save file
        save_path = self.file_path_entry.get().strip()
        if save_path:
            # Save the file to the specified path
            # self.ctx.client.publish_file(self.file_path, save_path)
            messagebox.showinfo("Success", "File saved successfully!")
            self.destroy()
        else:
            messagebox.showerror(
                "Error", "Please enter a valid file path.", parent=self
            )


class LogTab(ttk.Frame):
    def __init__(self, parent):
        # Initialize the log tab
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self) -> None:
        # Create widgets for the log tab
        # Create a frame to hold the log text and refresh button
        log_frame = ttk.Frame(self, borderwidth=2, relief="raised")
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create a label for the log text
        log_label = ttk.Label(log_frame, text="Log Entries", font=("Times New Roman", 15, "bold"))
        log_label.pack(side=tk.TOP, padx=10, pady=(10, 5))

        # Add button to fetch logs
        self.refresh_button = ttk.Button(
            log_frame, text="Reset", command=self.fetch_logs, style="Custom.TButton"
        )
        self.refresh_button.pack(side=tk.LEFT, padx=10, pady=(20, 10), anchor="ne")

        # Create a Text widget to display logs
        self.log_text = tk.Text(log_frame, wrap="word", font=("Courier", 10))
        self.log_text.pack(side=tk.LEFT, expand=True, fill="both", padx=(10, 0), pady=10)

        # Create a scrollbar for the Text widget
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.style = ttk.Style()
        self.style.configure("Log.TText", font=("Courier", 10))
        #self.log_text.configure(style="Log.TText")

    def fetch_logs(self):
        # Function to fetch logs
        # Get logs from server
        logs = self.parent.server.get_log()

        # Clear existing log text
        self.log_text.delete("1.0", tk.END)

        # Insert new log entries
        for entry in logs:
            self.log_text.insert(tk.END, f"{entry}\n")


# if __name__ == "__main__":
#     # Create and run the main application
#     app = MainApplication()
#     app.mainloop()
if __name__ == "__main__":
    server = tracking_server()
    magnet_text = "alice"
    server.file_client[magnet_text] = ["1.1.1.1", "10.1.1.1"]
    server.client_servers = {"1.1.1.1": 9090, "10.1.1.1": 2000, "2.1.41.2": 6969}
    magnet_text_test = "alice"
    send_data = ""
    if magnet_text_test in server.file_client:
        # Process peers dictionary
        peers_info = {}
        clients_ip = server.file_client[magnet_text_test]
        ports = []

        for client in clients_ip:
            ports.append(server.client_servers[client])

        # peers_info['id'] = f"{clientIP}:{clientPort}"
        peers_info['ip'] = clients_ip
        peers_info['port'] = ports

        send_data = "[Anouncement]--Download Successfully--"  # Split by --
        send_data += f"{peers_info}"

        server.file_client[magnet_text_test].append('9.9.9.9')
        print(send_data)

    split_data = send_data.split("--")

    announcement = split_data[0]
    success_message = split_data[1]
    peer_info = eval(split_data[2])  # Use eval to convert the string representation of dictionary back to dictionary

    print(announcement)
    print(success_message)
    print(peer_info)

    print("=======")
    peer_info['ip'].remove("1.1.1.1")
    print(peer_info)
