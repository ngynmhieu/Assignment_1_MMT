import sys
from torrent import *
import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify
import json
from threading import Thread

class Peer:
    def __init__(self, ip, port, peer_id, torrent):
        self.ip = ip
        self.port = port
        self.peer_id = peer_id
        self.torrent = torrent
        self.bitfield = ''
    def get_ip(self):
        return self.ip
    def get_port(self):
        return self.port
    def get_peer_id(self):
        return self.peer_id
    def get_torrent(self):
        return self.torrent
    def get_bitfield(self):
        return self.bitfield
    def set_bitfield(self, bitfield):
        self.bitfield = bitfield

def verify_data_left(location, torrent):
    
    length = 0
    if 'files' in torrent.get_info():
        for file in torrent.get_info()['files']:
            length += file[b'length']
    else:
        length = torrent.get_info()['length']
        
    files = os.listdir(location[0])
    
    for file in files:
        path = os.path.join(location[0], file)
        if 'files' in torrent.get_info(): #multiple files torrent
            
            for file_info in torrent.get_info()['files']:
                if file_info[b'path'][0].decode() == file:
                    with open(path, 'rb') as f:
                        data = f.read()
                        length -= len(data)
                    break
        else: #single file torrent
            if torrent.get_info()['name'] == file:
                with open(path, 'rb') as f:
                    data = f.read()
                    length -= len(data)
                break
    
    torrent.set_left(length)
    return

def split_pieces_and_hash(location, torrent):
    #todo
    all_data = b''
    files = os.listdir(location[0])
    
    for file in files:
        path = os.path.join(location[0], file)
        if 'files' in torrent.get_info(): #multiple files torrent
            for file_info in torrent.get_info()['files']:
                if file_info[b'path'][0].decode() == file:
                    with open(path, 'rb') as f:
                        data = f.read()
                        all_data += data
                    break
        else: #single file torrent
            if torrent.get_info()['name'] == file:
                with open(path, 'rb') as f:
                    data = f.read()
                    all_data += data
                break
    pieces = [all_data[i:i+torrent.get_piece_length()] for i in range(0, len(all_data), torrent.get_piece_length())]
    sha1_hashes = [hashlib.sha1(piece).digest() for piece in pieces]
    return sha1_hashes
    
def generate_bitfield(location, torrent):
    bitfield = ''
    hash_pieces = split_pieces_and_hash(location, torrent)
    # print (hash_pieces, '\n')
    for torrent_piece, hash_piece in zip(torrent.get_pieces(), hash_pieces):
        if torrent_piece == hash_piece:
            bitfield += '1'
        else:
            bitfield += '0'
    return bitfield