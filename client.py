from pathlib import Path

read_buffer_size = 1024
chunk_size = 1024 * 100


def _chunk_file(file, extension, output_folder_path):
    current_chunk_size = 0
    current_chunk = 1
    done_reading = False
    while not done_reading:
        with open(f'{output_folder_path}/{current_chunk}{extension}.chk', 'ab') as chunk:
            while True:
                bfr = file.read(read_buffer_size)
                if not bfr:
                    done_reading = True
                    break

                chunk.write(bfr)
                current_chunk_size += len(bfr)
                if current_chunk_size + read_buffer_size > chunk_size:
                    current_chunk += 1
                    current_chunk_size = 0
                    break


def _split(file_path, output_folder_path):
    p = Path(file_path)
    if  p.exists():
        with open(p, 'rb') as file:
            _chunk_file(file, p.suffix, output_folder_path)


def _join(folder_path, output_file_path):
    p = Path(folder_path)
    chunks = list(p.rglob('*.chk'))
    chunks.sort()
    extension = chunks[0].suffixes[0]
    with open(f'{output_file_path}/join{extension}', 'ab') as file:
        for chunk in chunks:
            with open(chunk, 'rb') as piece:
                while True:
                    bfr = piece.read(read_buffer_size)
                    if not bfr:
                        break
                    file.write(bfr)


zip_file_path = '/content/drive/MyDrive/Bosch data/stop.png'
zip_output_path = '/content/drive/MyDrive/computer network'
output_folder = '/content/drive/MyDrive/computer network/output_chunks'
_split(zip_file_path, output_folder)
_join(output_folder, zip_output_path)
# chunk_size = 1024*10
# file_size = os.path.getsize(zip_file_path)
# chunks = create_chunks_from_zip(zip_file_path, chunk_size, output_folder, file_size)
# # Modify chunks as needed
# output_zip_file_path = '/content/drive/MyDrive/computer network/alice_output.zip'

# merge_chunks_to_zip(output_folder, output_zip_file_path, file_size)

import os
import socket

LOCAL_PORT = 22822
SERVER_PORT = 12345

class File:
    def __init__(self):
        self.path = ""
        self.size = self.get_file_size(self.path)
        self.chunk = self.get_total_chunk()
        self.chunkDict = {}

    def get_file_size(self, path):
        return os.path.getsize(path)
    def get_total_chunk(self):
        # Use for upload client only
        total_chunk = 0

        return total_chunk

    def merge_chunk(self):
        return

    def is_enough(self):
        return len(self.chunkDict) == self.chunk

class client:
    def __init__(self):
        self.file_list = []
        self.client_host = self.get_local_ip()
        self.client_port = LOCAL_PORT
        self.server_host = ""
        self.server_port = SERVER_PORT
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message = ""
        self.log = []
        self.upload_path = ""
        self.download_path = ""

    def get_local_ip(self):
        try:
            # Create a socket object and connect to an external server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))  # Google's public DNS server and port 80
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error as e:
            return f"Unable to determine local IP: {str(e)}"

    def set_server_host(self, host):
        self.server_host = host

    def set_client_upload_path(self, path):
        self.upload_path = path

    def set_client_download_path(self, path):
        self.download_path = path

    def set_message(self, message):
        self.message = message

    def get_server_host(self):
        return self.server_host

    def get_client_host(self):
        return self.client_host

    def get_download_dir(self):
        return self.download_path

    def get_upload_dir(self):
        return self.upload_path

    def get_message(self):
        return self.message

    def get_files_list(self):
        return self.file_list

    def send_chunk_to_client(self, clientInfo):
        return

    def receive_chunk_from_client(self, clientInfo):
        return

    def handle_server(self, connection, address):
        return

    def start_client(self):
        return