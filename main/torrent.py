import bencodepy
import os
import hashlib
from collections import OrderedDict
import tkinter as tk
from tkinter import filedialog
import bittorent_client
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
    



# tao file torrent tu file_path
def create_torrent(file_path, piece_length):
    piece_length = piece_length*1024;
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # chia file thanh tung manh 512 KB
    pieces = [file_data[i:i+piece_length] for i in range(0, len(file_data), piece_length)]
    sha1_hashes = b''.join(hashlib.sha1(piece).digest() for piece in pieces)

    torrent_info = {
        'length': os.path.getsize(file_path),
        'name': os.path.basename(file_path),
        'piece length': piece_length,  # Kích thước phần là 512KB
        'pieces': sha1_hashes
    }
    
    torrent = {
        'announce': 'tracker.py',
        'info': torrent_info
    }
    torrent_bencoded = bencodepy.encode(torrent)
    with open('C:/Users/Minh Hieu/OneDrive/Desktop/MMT_A1/Assignment_1_MMT/main/testing/test.torrent', 'wb') as f:
        f.write(torrent_bencoded)
      
# Read torrent file
def read_torrent_file(file_path):
    with open(file_path, 'rb') as f:
        torrent_data = bencodepy.decode(f.read())
    announce = torrent_data[b'announce'].decode('utf-8')
    info_temp = torrent_data[b'info']
    infor_temp = OrderedDict(info_temp)
    
    info = dict(infor_temp)
    info = {key.decode('utf-8'): (value if key == b'pieces' else value.decode('utf-8', errors='ignore')) if isinstance(value, bytes) else value for key, value in info.items()}
    
    return Torrent(announce, info)

#import and create torrent file from browser
def open_file(root, filepath):
    filepath.append(filedialog.askopenfilename())
    print(f"Open: {filepath[0]}")
    root.destroy()

def import_file():
    root = tk.Tk()
    filepath = []
    button = tk.Button(root, text="Mở tệp", command=lambda: open_file(root, filepath))
    button.pack()
    root.mainloop()
    return filepath[0]
    
def ImAndCreate():
    filepath = import_file()
    create_torrent(filepath, 256)
    print("Successfully create torrent file")

#Peer asking to participate in tracker network        
