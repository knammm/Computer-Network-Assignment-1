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