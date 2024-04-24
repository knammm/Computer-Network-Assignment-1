from pathlib import Path
import os
import json
import socket
import math
import random
import time

kilobytes = 1024
chunksize = kilobytes * 100
readsize = kilobytes
BYTES = 102400

LOCAL_PORT = 22822
SERVER_PORT = 12345
FILE_PORT = 228223

class Chunk:
    chunks_dict = {}

    # init function
    def __init__(self, name, total):
        self.name = name
        self.total = total
        self.number_of_chunk = 0
        self.chunks_dict = {}

    def add_chunk(self, order, data):
        if order not in self.chunks_dict:
            self.number_of_chunk += 1
        self.chunks_dict[order] = data

    def find_chunk(self, order):
        return self.chunks_dict[order]

    def delect_chunk(self, order):
        if order in self.chunks_dict:
            self.number_of_chunk -= 1
            self.chunks_dict.pop(order)

    def print_chunks(self):
        for i in self.chunks_dict.keys():
            print(self.chunks_dict[i])
            print(f"key {i}: {self.chunks_dict[i]}")

    def isComplete(self):
        return self.total == self.number_of_chunk

    def split_chunks(self, id, fromfile, todir):
        if not os.path.exists(todir):  # caller handles errors
            os.mkdir(todir)  # make dir, read/write parts
        else:
            for fname in os.listdir(todir):  # delete any existing files
                os.remove(os.path.join(todir, fname))
        partnum = 0
        input = open(fromfile, 'rb')  # use binary mode on Windows
        while 1:  # eof=empty string from read
            chunk = input.read(chunksize)  # get next part <= chunksize
            if not chunk: break
            partnum = partnum + 1
            filename = os.path.join(todir, (f'{id}_{partnum}.txt'))
            header = f"{id} {partnum}\n".encode()
            fileobj = open(filename, 'wb')
            fileobj.write(header)
            fileobj.write(chunk)
            self.add_chunk(partnum, filename)
            fileobj.close()  # or simply open(  ).write(  )
        input.close()
        return partnum

    def merge_chunks(self, tofile):
        output = open(tofile, 'wb')
        for order in range(self.total):
            filepath = self.chunks_dict[order + 1]
            with open(filepath, 'rb') as fileobj:
                fileobj.readline()
                while 1:
                    filebytes = fileobj.read(readsize)
                    if not filebytes: break
                    output.write(filebytes)
                fileobj.close()
        output.close()


class Client_dict:
    dict = {}

    def __init__(self):
        self.dict = {}

    def add_file(self, file_id, file_name, total):
        if file_id not in self.dict:
            self.dict[file_id] = Chunk(file_name, total)
        else:
            if self.dict[file_id].name == "undefined":
                self.dict[file_id].name = file_name
                self.dict[file_id].total = total

    def delete_file(self, file_id):
        self.dict.pop(file_id)

    def add_chunk(self, file_id, path, order):
        if file_id not in self.dict:
            self.add_file(file_id, "undefined", 9999)
        self.dict[file_id].add_chunk(order, path)
        return 0

    def add_undefine_chunk(self, path):
        with open(path, 'rb') as fileobj:
            first_line = fileobj.readline()
            id, order = first_line.split()
            self.add_chunk(int(id), path, int(order))

    def delete_chunk(self, file_id, order):
        if file_id in self.dict:
            self.dict[file_id].delect_chunk(order)

    def print_dict(self):
        for i in self.dict.keys():
            print(f"file id:{i}, file name: {self.dict[i].name}, total: {self.dict[i].total}")
            print(f"number of current chunks: {self.dict[i].number_of_chunk}")
            for j in self.dict[i].chunks_dict.keys():
                print(f"-----order {j}: {self.dict[i].chunks_dict[j]}")

    def is_complete(self, file_id):
        return self.dict[file_id].isComplete()

    def missing_file(self, file_id):
        list_of_missing = []
        stop = self.dict[file_id].total
        for i in range(stop):
            if i not in self.dict[file_id].chunks_dict:
                list_of_missing.append(i)
        return list_of_missing

    def create_JSON(self, id, dirpath):
        file_info = {}
        if id in self.dict:
            file_info['id'] = id
            file_info['name'] = self.dict[id].name
            file_info['total'] = self.dict[id].total
        json_file_path = f'{dirpath}\{self.dict[id].name}.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(file_info, json_file, indent=4)
        return json_file_path

    def add_file_from_JSON(self, JSONpath):
        with open(JSONpath, 'r') as json_file:
            file_info = json.load(json_file)
            self.add_file(file_info.get("id"), file_info.get("name"), file_info.get("total"))

    def merge(self, other_client_dict: 'Client_dict'):
        for i in other_client_dict.dict.keys():
            if i not in self.dict:
                self.add_file(i, other_client_dict.dict[i].name, other_client_dict.dict[i].total)
            for j in other_client_dict.dict[i].chunks_dict.keys():
                self.add_chunk(i, other_client_dict.dict[i].chunks_dict[j], j)

    def split_chunks(self, id, fromfile, todir):
        name = os.path.basename(fromfile)
        filesize = os.path.getsize(fromfile)
        total = math.ceil(filesize / chunksize)
        self.add_file(id, name, total)
        self.dict[id].split_chunks(id, fromfile, todir)

    def merge_chunks(self, id, tofile):
        if self.is_complete(id):
            self.dict[id].merge_chunks(tofile)


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
        self.client_socket.connect((self.get_server_host(), SERVER_PORT))

        while True:
            receive_message = self.client_socket.recv(BYTES).decode("utf-8")
            msg_split = receive_message.split("--")
            cmd = msg_split[1]

            if "Welcome" in cmd:
                self.client_socket.send(f'{LOCAL_PORT}'.encode("utf-8"))

            elif "Download" in cmd:
                print(receive_message)

                if len(msg_split) == 4:
                    # Get information
                    file_info = eval(msg_split[2]) # convert back to dict
                    peer_info = eval(msg_split[3])

                    # Random choose a client to connect
                    rand_int = random.randint(0, len(peer_info['ip']) - 1)
                    connect_tuple = (peer_info['ip'][rand_int], peer_info['port'][rand_int])
                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_socket.connect(connect_tuple)

                    # Apply sending chunk algorithm here...

                    # Close connection
                    new_socket.close()

                self.log.append(receive_message)


            elif "Disconnect" in cmd:
                self.log.append(receive_message)
                break

            else:
                self.log.append(receive_message)

            time.sleep(0.1)

            client_cmd = self.get_message()
            if client_cmd == " ":
                client_cmd = "Waiting"
            cmd_split = client_cmd.split(" ")
            cmd = cmd_split[0]

            if cmd == "Upload" and (len(cmd_split) == 3):
                magnet_text = cmd_split[1]
                contents = cmd_split[2]
                send_data = f"Upload {magnet_text} {contents}"
                self.client_socket.send(send_data.encode("utf-8"))
                self.set_message(" ")

            elif cmd == "Download" and (len(cmd_split) == 2):
                self.client_socket.send(cmd.encode("utf-8"))
                self.set_message(" ")

            elif cmd == "Disconnect":
                self.client_socket.send(cmd.encode("utf-8"))

            elif cmd == "Waiting":
                self.client_socket.send(cmd.encode("utf-8"))
                self.set_message(" ")

            else:
                cmd = "Wrong"
                self.client_socket.send(cmd.encode("utf-8"))
                self.set_message(" ")

        self.log.append("[Anncounment] Disconnect from the server !")
        self.client_socket.close()

    def start_client(self):
        return


if __name__ == '__main__':
    client_dict = Client_dict()
    other_client_dict = Client_dict()
    other_client_dict.add_file(0, "file0.txt", 5)
    client_dict.add_file(1, "file1.zip", 3)
    client_dict.add_file(3, "file3.png", 5)

    # print(client_dict.dict.values())
    chunk_test = Chunk("test.txt", 10)
    chunk_test.add_chunk(1, "abcd")
    # chunk_test.print_chunks()
    other_client_dict.add_chunk(0, "file0-data2", 2)
    other_client_dict.add_chunk(0, "file0-data1", 1)

    client_dict.add_chunk(1, "file1-data4", 0)
    client_dict.add_chunk(1, "file1-data5", 1)
    client_dict.add_chunk(1, "file1-data2", 2)

    client_dict.add_chunk(3, "file3-data6", 6)
    client_dict.print_dict()
    client_dict.merge(other_client_dict)
    client_dict.print_dict()
    print(f"full:{client_dict.is_complete(1)}")
    print(f"Missing file:{client_dict.missing_file(1)}")
    zip_file_path = r'D:\Computer Network\BTL\testing_data\alice.zip'
    zip_output_path = r'D:\Computer Network\BTL\testing_data\alice_out.zip'
    output_folder = r'D:\Computer Network\BTL\testing_data\output_chunks'
    output_json_folder = r'D:\Computer Network\BTL\testing_data'
    client_dict.add_undefine_chunk(r'D:\Computer Network\BTL\testing_data\clone_chunks.txt')
    client_dict.print_dict()
    client_dict.split_chunks(5, zip_file_path, output_folder)
    JSONpath = client_dict.create_JSON(5, output_json_folder)
    client_dict.add_file_from_JSON(JSONpath)
    client_dict.print_dict()
    client_dict.merge_chunks(5, zip_output_path)