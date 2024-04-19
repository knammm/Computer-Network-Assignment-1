from pathlib import Path

read_buffer_size = 1024
chunk_size = 1024 * 100

# class Chunks_data:
#     def __init__(self, data = None, size = 0):
#         self.data = data
#         self.size = size
    
#     def clear_data(self):
#         self.data = None
#         self.size = 0
    
#     def add_data(self, data, data_size):
#         self.data = data
#         self.size = data_size

class Chunk:
    chunks_dict = {}
    #init function
    def __init__(self, name, suffix, total):
        self.name = name
        self.suffix = suffix
        self.total_chunk = total
        self.number_of_chunk = 0
        self.chunks_dict = {}

    def add_chunk(self, order, data):
        if order in self.chunks_dict:
            self.number_of_chunk += 1
        self.chunks_dict[order] = data

    def find_chunk(self, order):
        return self.chunks_dict[order]
    
    def delect_chunk(self, order):
        if self.chunks_dict[order]:
            self.number_of_chunk -= 1
            self.chunks_dict.pop(order)

    def print_chunks(self):
        for i in self.chunks_dict.keys():
            print(self.chunks_dict[i])
            print(f"key {i}: {self.chunks_dict[i]}")

class Client_dict:
    dict = {}
    def __init__(self):
        self.number_of_file = 0
        self.dict = {}

    def add_file(self, file_id, file_name, suffix, total):
        self.dict[file_id] = Chunk(file_name, suffix, total)

    def delete_file(self, file_id):
        self.dict.pop(file_id)

    def add_chunk(self, file_id, data, order):
        if file_id in self.dict:
            print("File is not exist!")
            return 0
        else:
            print(self.dict[file_id])
            self.dict[file_id].add_chunk(order, data)

    def print_dict(self):
        for i in self.dict.keys():
            print(f"file id:{i}, file name: {self.dict[i].name}{self.dict[i].suffix}\n")
            for j in self.dict[i].chunks_dict.keys():
                print(f"-----order {j}: {self.dict[i].chunks_dict[j]}\n")



def chunk_create(file, extension, output_folder_path):
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


def create_chunk(file_path, output_folder_path):
    p = Path(file_path)
    if  p.exists():
        with open(p, 'rb') as file:
            chunk_create(file, p.suffix, output_folder_path)


def merge_chunk(folder_path, output_file_path):
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


# zip_file_path = r'D:\Computer Network\BTL\testing_data\alice.zip'
# zip_output_path = r'D:\Computer Network\BTL\testing_data'
# output_folder = r'D:\Computer Network\BTL\testing_data\output_chunks'
# create_chunk(zip_file_path, output_folder)
# merge_chunk(output_folder, zip_output_path)
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
    

client_dict = Client_dict()
client_dict.add_file(0, "file0", ".txt", 5)
client_dict.add_file(1, "file1", ".zip", 3)
client_dict.add_file(3, "file3", ".png", 5)

# print(client_dict.dict.values())
chunk_test = Chunk("test", ".txt", 10)
chunk_test.add_chunk(1, "abcd")
# chunk_test.print_chunks()
client_dict.add_chunk(0, "file0-data2", 2)
client_dict.add_chunk(0, "file0-data1", 1)

client_dict.add_chunk(1, "file1-data4", 4)
client_dict.add_chunk(1, "file1-data5", 5)
client_dict.add_chunk(1, "file1-data2", 2)

client_dict.add_chunk(3, "file3-data6", 6)

client_dict.print_dict()
