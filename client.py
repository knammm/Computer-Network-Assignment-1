import os
import json
import socket
import math
import random
import time
import threading

kilobytes = 1024
chunksize = kilobytes * 100
readsize = kilobytes
BYTES = 102400

LOCAL_PORT = 22822
SERVER_PORT = 18520
# FILE_PORT = 228223

id_download = {}
id_upload = {}
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
    
    def add_chunks_from_dir(self, dir, id):
        all_files = os.listdir(dir)
        chunk_files = [file for file in all_files if file.startswith(f'{id}_')]
        for filename in chunk_files:
            filepath = f"{dir}\{filename}"
            with open(filepath, 'rb') as fileobj:
                content = fileobj.readline()
                values = content.split()
                self.add_chunk(id, filepath, int(values[1]))

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
            self.add_file(int(file_info.get("id")), file_info.get("name"), int(file_info.get("total")))
            return int(file_info.get("id"))

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

general_dict = Client_dict()

class client:
    def __init__(self):
        self.file_list = Client_dict()
        self.client_host = self.get_local_ip()
        self.client_port = LOCAL_PORT
        self.server_host = ""
        self.server_port = SERVER_PORT
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message = ""
        self.log = []
        self.upload_path = ""
        self.download_path = ""
        self.json_path = ""
        self.chunk_path = ""
        self.id = -1
        self.status = 0

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

    def send_chunk_to_client(self, clientConnect, clientSocket):
        print(f'Prepare to serve {clientSocket}...')
        receive_message = clientConnect.recv(BYTES).decode("utf-8")
        uniqueID = receive_message.split("--")[0]
        start = receive_message.split("--")[1]
        chunk_files = os.listdir(self.chunk_path)
        correct_chunk_files = [file for file in chunk_files if file.startswith(f'{uniqueID}_')]
        print(correct_chunk_files)
        clientConnect.send(f"{len(correct_chunk_files)}".encode("utf-8")) # send file count
        correct_path = []
        # Always make the file order ascendingly
        sorted_file_names = sorted(correct_chunk_files, key=lambda x: int(x.split('_')[1].split(".")[0]))
        for file in sorted_file_names:
            correct_path.append(self.chunk_path + '\\' + file)

        for i in range(start - 1, len(correct_chunk_files)):
            with open(correct_chunk_files[i], "rb") as f:
                text = f.read()
                clientConnect.sendall(text)

            status_file = clientConnect.recv(BYTES).decode("utf-8")

            if status_file == "OK":
                print("Continue")
            else:
                print("Fail")
                break

        time.sleep(2)

    def open_file_serving_socket(self):
        self.file_soket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.get_client_host())
        try:
            self.file_soket.bind(("192.168.32.104", LOCAL_PORT))
            
        except:
            print("Something went wrong")

        self.file_soket.listen()
        print(f"The file serving socket is {self.file_soket.getsockname()}")
        while True:
            try:
                peer_client, peer_client_socket = self.file_soket.accept()
                s_file_client = threading.Thread(target=self.send_chunk_to_client, args=(peer_client, peer_client_socket))
                s_file_client.start()
            except:
                pass

    def handle_server(self):
        self.client_socket.connect((self.get_server_host(), SERVER_PORT))

        while True:
            receive_message = self.client_socket.recv(BYTES).decode("utf-8")
            msg_split = receive_message.split("--")
            cmd = msg_split[1]

            if "Welcome" in cmd:
                self.client_socket.send(f'{LOCAL_PORT}'.encode("utf-8"))

            elif "Upload Successfully" in cmd:
                print(receive_message)  

                if len(msg_split) == 3:
                    uniqueID = int(msg_split[2]) # Get unique ID
                    name = os.path.basename(self.upload_path)
                    total_chunks = os.path.getsize(self.upload_path)/chunksize
                    general_dict.add_file(uniqueID, name, total_chunks)
                    general_dict.split_chunks(uniqueID, self.upload_path, self.chunk_path)
                self.log.append(receive_message)
                print(f"Upload successfully {uniqueID}")

            elif "Download Successfully" in cmd:
                print(receive_message)

                if len(msg_split) == 4:
                    # Get information
                    self.id = int(msg_split[2])
                    peer_info = eval(msg_split[3])

                    # Initialize message
                    chunkIdx = 1
                    while True:
                        # Random choose a client to connect
                        rand_int = random.randint(0, len(peer_info['ip']) - 1)
                        miniServerIP = peer_info['ip'][rand_int]
                        miniServerPort = peer_info['port'][rand_int]
                        connect_tuple = (miniServerIP, miniServerPort) # connect client
                        # Pop connected client out of list
                        peer_info['ip'].remove(miniServerIP)
                        peer_info['port'].remove(miniServerPort)
                        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            new_socket.connect(connect_tuple)

                            new_socket.send(f"{self.id}--{chunkIdx}".encode("utf-8")) # Send uniqueID--chunkStart
                            size = new_socket.recv(BYTES).decode("utf-8")

                            for i in range(0, int(size)):
                                path = self.chunk_path + "\\" + f"{self.id}_{chunkIdx}.txt"
                                print(path)
                                text = new_socket.recv(BYTES)
                                try:
                                    with open(path, 'wb') as file:
                                        file.write(text)
                                    print(f"Text file '{path}' created successfully.")
                                    new_socket.send(f"OK".encode("utf-8"))
                                except IOError as e:
                                    print(f"Error: {e}")
                                    new_socket.send(f"Fail".encode("utf-8"))
                                    chunkIdx -= 1
                                    break
                                file.close()
                                chunkIdx += 1

                            total = 0 # Change to total chunk
                            # Handle enough chunk => break
                            if (chunkIdx - 1) == total:
                                print("Success")
                                self.status = 1
                                id = general_dict.add_file_from_JSON(self.json_path)
                                general_dict.add_chunks_from_dir(self.chunk_path, id)
                                general_dict.merge_chunks(id, self.download_path)
                                break

                            if chunkIdx < total:
                                if len(peer_info['ip']) == 0:
                                    # case : no peer has enough chunk
                                    print("Fail - No peer have enough chunk")
                                    # removing chunk files
                                    files = os.listdir(self.chunk_path)
                                    self.status = -1
                                    for file in files:
                                        if file.startswith(f"{self.id}_"):
                                            os.remove(os.path.join(self.chunk_path, file))
                                    break

                            # Close connection
                            new_socket.close()
                        except:
                            print(f"Fail to connect to {connect_tuple}")
                            pass

                    print("Finished")

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

            if cmd == "Upload":
                send_data = f"Upload"
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
        t1 = threading.Thread(target=self.handle_server)
        t1.start()
        t2 = threading.Thread(target=self.open_file_serving_socket)
        t2.start()
        return

new_client = client()



if __name__ == '__main__':
    uniqueID = "5"
    # send_data = data
    # clientConnect.send(f"{send_data}".encode("utf-8"))
    # dir = r'D:\BKU - K21 - Computer Engineering\Computer Network\Assignment\Assignment 1\git\testing_data\output_chunks'
    # chunk_files = os.listdir(dir)
    # print(chunk_files)
    # correct_chunk_files = [file for file in chunk_files if file.startswith(f'{uniqueID}')]
    # print(correct_chunk_files)
    # correct_path = []
    # sorted_file_names = sorted(correct_chunk_files, key=lambda x: int(x.split('_')[1].split(".")[0]))
    # for file in sorted_file_names:
    #     correct_path.append(dir + '\\' + file)

    # print(len(correct_path))

    # for path in correct_path:
    #     print(path)
    new_client.set_client_download_path(r"D:\Computer Network\BTL\testing_data")
    new_client.set_client_upload_path(r"D:\Computer Network\BTL\testing_data\alice.zip")
    new_client.chunk_path = r"D:\Computer Network\BTL\testing_data\output_chunks"
    new_client.json_path = "D:\Computer Network\BTL\testing_data\alice.zip.json"
    new_client.set_server_host("192.168.32.104")
   
    
    new_client.start_client()
    while(1):
        new_client.set_message("Upload")
    # size = 20
    # ID = uniqueID
    # for i in range(1, int(size) + 1):
    #     path = dir + "\\" + f"{ID}_{i}.txt"
    #     text = "ABC"
    #     try:
    #         with open(path, 'w') as file:
    #             file.write(text)
    #         print(f"Text file '{path}' created successfully.")
    #     except IOError as e:
    #         print(f"Error: {e}")