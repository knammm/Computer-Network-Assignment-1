from pathlib import Path
import sys, os

kilobytes = 1024
chunksize = kilobytes*100
readsize = kilobytes

class Chunk:
    chunks_dict = {}
    #init function
    def __init__(self, name, suffix, total):
        self.name = name
        self.suffix = suffix
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

class Client_dict:
    dict = {}
    def __init__(self):
        self.dict = {}

    def add_file(self, file_id, file_name, suffix, total):
        self.dict[file_id] = Chunk(file_name, suffix, total)

    def delete_file(self, file_id):
        self.dict.pop(file_id)

    def add_chunk(self, file_id, data, order):
        if file_id in self.dict:
            self.dict[file_id].add_chunk(order, data)
        else:
            print("File is not exist!")
            return 0
    
    def delete_chunk(self, file_id, order):
        if file_id in self.dict:
            self.dict[file_id].delect_chunk(order)

    def print_dict(self):
        for i in self.dict.keys():
            print(f"file id:{i}, file name: {self.dict[i].name}{self.dict[i].suffix}, total: {self.dict[i].total}")
            print(f"number of current chunks: {self.dict[i].number_of_chunk}")
            for j in self.dict[i].chunks_dict.keys():
                print(f"-----order {j}: {self.dict[i].chunks_dict[j]}")

    def isComplete(self, file_id):
        return self.dict[file_id].isComplete()
    
    def missingFile(self, file_id):
        list_of_missing = []
        stop = self.dict[file_id].total
        for i in range(stop):
            if i not in self.dict[file_id].chunks_dict:
                list_of_missing.append(i)
        return list_of_missing
    
    def merge(self, other_client_dict : 'Client_dict'):
        for i in other_client_dict.dict.keys():
            if i not in self.dict:
              self.add_file(i, other_client_dict.dict[i].name, other_client_dict.dict[i].suffix, other_client_dict.dict[i].total)
            for j in other_client_dict.dict[i].chunks_dict.keys():
                self.add_chunk(i, other_client_dict.dict[i].chunks_dict[j], j)



def split_chunks(fromfile, todir, chunksize=chunksize): 
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts
    else:
        for fname in os.listdir(todir):            # delete any existing files
            os.remove(os.path.join(todir, fname)) 
    partnum = 0
    input = open(fromfile, 'rb')                   # use binary mode on Windows
    while 1:                                       # eof=empty string from read
        chunk = input.read(chunksize)              # get next part <= chunksize
        if not chunk: break
        partnum  = partnum+1
        filename = os.path.join(todir, ('part%04d.txt' % partnum))
        fileobj  = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()                            # or simply open(  ).write(  )
    input.close(  )
    assert partnum <= 9999                         # join sort fails if 5 digits
    return partnum

def join_chunks(fromdir, tofile):
    output = open(tofile, 'wb')
    parts  = os.listdir(fromdir)
    parts.sort(  )
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close(  )
    output.close(  )

if __name__ == '__main__':
    client_dict = Client_dict()
    other_client_dict = Client_dict()
    other_client_dict.add_file(0, "file0", ".txt", 5)
    client_dict.add_file(1, "file1", ".zip", 3)
    client_dict.add_file(3, "file3", ".png", 5)

    # print(client_dict.dict.values())
    chunk_test = Chunk("test", ".txt", 10)
    chunk_test.add_chunk(1, "abcd")
    # chunk_test.print_chunks()
    other_client_dict.add_chunk(0, "file0-data2", 2)
    other_client_dict.add_chunk(0, "file0-data1", 1)

    client_dict.add_chunk(1, "file1-data4", 0)
    client_dict.add_chunk(1, "file1-data5", 1)
    client_dict.add_chunk(1, "file1-data2", 2)

    # client_dict.delete_chunk(1, 2)

    client_dict.add_chunk(3, "file3-data6", 6)
    client_dict.print_dict()
    client_dict.merge(other_client_dict)
    client_dict.print_dict()
    print(f"full:{client_dict.isComplete(1)}")
    print(f"Missing file:{client_dict.missingFile(1)}")
    # client_dict.print_dict()
    # zip_file_path = r'D:\Computer Network\BTL\testing_data\alice.zip'
    # zip_output_path = r'D:\Computer Network\BTL\testing_data\alice_out.zip'
    # output_folder = r'D:\Computer Network\BTL\testing_data\output_chunks'
    # # create_chunk(zip_file_path, output_folder)
    # # merge_chunk(output_folder, zip_output_path)
    # split_chunks(zip_file_path, output_folder)
    # join_chunks(output_folder, zip_output_path)