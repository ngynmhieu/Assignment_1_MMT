import bencodepy
import os
import hashlib

# Kieu du lieu torrent

class Torrent:
    def __init__(self, announce, info):
        self.announce = announce
        self.length = info.get('length')
        self.name = info.get('name')
        self.piece_length = info.get('piece length')
        self.pieces = info.get ('pieces')
    
    def get_announce(self):
        return self.announce
    def get_length(self):
        return self.length
    def get_name(self):
        return self.name
    def get_piece_length(self):
        return self.piece_length
    def get_pieces(self):
        return self.pieces
    



# tao file torrent (chi can thong tin cua file)
def create_torrent(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    sha1_hash = hashlib.sha1(file_data).digest()

    torrent_info = {
        'length': os.path.getsize(file_path),
        'name': os.path.basename(file_path),
        'piece length': 524288,  # Kích thước phần là 512KB
        'pieces': sha1_hash
    }
    
    torrent = {
        'announce': 'tracker.py',
        'info': torrent_info
    }
    torrent_bencoded = bencodepy.encode(torrent)
    with open('test.torrent', 'wb') as f:
        f.write(torrent_bencoded)
        
        
def torrent_to_text(torrent_file_path, text_file_path):
    # Read the torrent file
    with open(torrent_file_path, 'rb') as f:
        content = f.read()

    # Decode the content using bencode
    metainfo = bencodepy.decode(content)

    # Write the metainfo to a text file
    with open(text_file_path, 'w') as f:
        for key, value in metainfo.items():
            f.write(f"{key}: {value}//n")

# Sử dụng hàm
# create_torrent('test.pdf')
torrent_to_text('test.torrent', 'test.txt')







# class TorrentFile:
#     def __init__(self, announce, info_file, length, name, piece_length, pieces):
#         self.announce = announce
#         self.info_file = info_file
#         self.length = length
#         self.name = name
#         self.piece_length = piece_length
#         self.pieces = pieces


# Call the function with a sample torrent file and a text file
# # torrent_to_text("sample.torrent", "output.txt")  # Uncomment this line and replace "sample.torrent" and "output.txt" with your actual file paths


# torrent_to_text("YoloHome___AIoT_v2.torrent", "C:/Users/Minh Hieu/OneDrive/Desktop/MMT_A1/Assignment_1_MMT/test.txt")