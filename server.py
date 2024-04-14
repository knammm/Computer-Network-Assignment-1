import socket
import time
import threading

BYTES = 102400

class tracking_server:
	def __init__(self):
		# Init socket properties
		self.host = self.get_local_ip()
		self.port = 12345

		# Init log
		self.log = [] # List of string
		self.log.append(f'[System Anouncement] Host is running at {self.host}, port {self.port}')

		# Init socket
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.bind((self.host, self.port)) # Tuple of (IP, Port)
		self.server_socket.listen()
		self.log.append(f'[System Anouncement] Server is running !')

		# Init other properties
		self.client_servers = {} # Key: peerIP - Value: port
		self.map_torrent = {} # Key: magnetText - Value: .torrentFile (JSON)
		self.file_client = {} # Key: fileName - Value: list of peers

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
		return self.client

	def get_available_files(self, address):
		# Function return a list of Files are available for the client address
		fileList = []
		for file in file_client.keys():
			if address in file_client[file]:
				fileList.append(file)

		return fileList 
			

	def handle_clients(self, connection, address):
		self.log.append(f'[System Anouncement] Accept new connection from {address} !')
		welcome_message = "Welcome to P2P File Sharing application !".encode("utf-8")
		connection.send(welcome_message)

		# Receive IP and port from client
		init_message = connection.recv(BYTES).decode("utf-8")
		init_message.split(" ")
		clientIP = init_message[0]
		clientPort = init_message[1]
		self.client_servers[clientIP] = clientPort

		while True:
			recv_message = connection.recv(BYTES).decode("utf-8")
			recv_message.split(" ") 
			client_cmd = recv_message[0]

			if client_cmd == 'Get':
				# Client sent 'Get'
				magnetText = recv_message[1]
				if magnetText in self.file_client:
					# Process peers dictionary
					peers_info = {}
					clients_ip = self.file_client[magnetText]
					ports = []

					for client in clients_ip:
						ports.append[client_servers[client]]

					# peers_info['id'] = ...
					peers_info['ip'] = clients_ip
					peers_info['port'] = ports

					send_data = "[Anouncement]--GET SUCCESSFULLY-- " # Split by space
					send_data += f"{peers_info}"
				else:
					send_data = "[Warning]--GET FAILED-- NO_FILE_FOUND"

				self.log.append(f"[System Anouncement] {clientIP}: Fetch")
				connection.send(send_data.encode("utf-8"))

			elif client_cmd == 'Upload':
				# Client sent 'Upload'
				pass

			elif client_cmd == 'Disconnect':
				# Client sent 'Disconnect'
				send_data = "[Disconnect]--Success--".encode("utf-8")
				connection.send(send_data)
				break

			elif client_cmd == 'Waiting':
				# Client did not send any massage -> refers to '\0'
				send_data = "[Warning]--Waiting for the command--".encode("utf-8")
				connection.send_data(send_data)

			else:
				send_message = f'[Warning]--Invalid Format--'.encode("utf-8")
				connection.send(send_message)

	def start_server(self):
		while True:
			try:
				clientSocket, clientAddress = self.server_socket.accept()
				clientCommand = threading.Thread(target=self.handle_clients, arg=(clientSocket, clientAddress))
				clientCommand.start()
			except:
				pass


if __name__ == "__main__":
	server = tracking_server()
	server.start_server()