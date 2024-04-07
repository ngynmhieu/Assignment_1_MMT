import bencode
import hashlib
import os

def create_torrent_file(file_path, tracker_url, torrent_file_name):
    # Function to calculate the SHA1 hash of a file
    def sha1_hash(file_path):
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # Read in 64k chunks
                if not data:
                    break
                sha1.update(data)
        return sha1.digest()

    # Check if the file exists
    if not os.path.exists(file_path):
        print("File not found.")
        return

    # Creating the metainfo dictionary
    metainfo = {}
    metainfo['announce'] = tracker_url
    metainfo['info'] = {}
    metainfo['info']['name'] = os.path.basename(file_path)
    metainfo['info']['length'] = os.path.getsize(file_path)
    metainfo['info']['piece length'] = 524288  # e.g., 512KB per piece
    metainfo['info']['pieces'] = sha1_hash(file_path)

    # Encoding the metainfo dictionary
    encoded_metainfo = bencode.bencode(metainfo)

    # Writing to a file
    with open(torrent_file_name, 'wb') as torrent_file:
        torrent_file.write(encoded_metainfo)

    print("Torrent file created successfully.")

# Example usage
create_torrent_file('file.txt', 'http://localhost:8080/announce', 'yourfile.torrent')
