import sys
from torrent import *
import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify, Response
import json
from threading import Thread
import operator
import math
import threading
import queue
import time
class Peer:
    def __init__(self, ip, port, peer_id, torrent, bitfield):
        self.ip = ip
        self.port = port
        self.peer_id = peer_id
        self.torrent = torrent
        self.bitfield = bitfield
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
        
def send_interested(peer_host, info_hash):
    intereseted_request = {'message': 'INTERESTED', 'info_hash': info_hash}
    response = requests.post(peer_host, data=json.dumps(intereseted_request))

    if response.status_code == 200:
        bitfield_response = json.loads(response.text)
        bitfield = bitfield_response.get('bitfield', '')
        print ('Received bitfield:', bitfield)
        return bitfield
    else:
        print ('Failed to send interested request.')

def verify_data_left(location, torrent):
    
    length = 0
    if 'files' in torrent.get_info():
        for file in torrent.get_info()['files']:
            length += file[b'length']
    else:
        length = torrent.get_info()['length']
        
    files = os.listdir(location[0])
    torrent.set_pieces_list (length, torrent.get_piece_length())
    torrent.set_hash_pieces_list (length, torrent.get_piece_length())
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

def split_pieces_and_hash(location, torrent, pieces_list, hash_pieces_list):
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
    pieces_list.clear()
    pieces_list.extend(pieces)
    sha1_hashes = [hashlib.sha1(piece).digest() for piece in pieces]
    hash_pieces_list.clear()
    hash_pieces_list.extend(sha1_hashes)
    return sha1_hashes
    
def generate_bitfield(location, torrent, pieces_list, hash_pieces_list):
    bitfield = ''
    hash_pieces = split_pieces_and_hash(location, torrent, pieces_list, hash_pieces_list)
    # print (hash_pieces, '\n')
    for torrent_piece, hash_piece in zip(torrent.get_pieces(), hash_pieces):
        if torrent_piece == hash_piece:
            bitfield += '1'
        else:
            bitfield += '0'
    print (f'Generated bitfield: {bitfield} successfully.')
    return bitfield

def calculate_piece_count(peer_list):
    piece_counts = {}
    for peer in peer_list:
        # Convert the bitfield string to a list of booleans
        bitfield = [bool(int(bit)) for bit in peer.get_bitfield()]
        for index, has_piece in enumerate(bitfield):
            if has_piece:
                if index in piece_counts:
                    piece_counts[index] += 1
                else:
                    piece_counts[index] = 1
    return piece_counts 


def download_block(peer, piece_index, block_length, block_queue, blocks_list):
    while True:
        try:
            # Get a block index from the queue
            block_index = block_queue.get(block=True, timeout=1)
            try:
                params ={
                    'info_hash': peer.get_torrent().get_info_hash(),
                    'peer_id': peer.get_peer_id(),
                    'piece_index': piece_index,
                    'block_index': block_index,
                    'block_length': block_length,
                }
                peer_host = 'http://' + peer.get_ip() + ':' + str(peer.get_port()) + '/download'
                print (f'Sending {block_index + 1}/{piece_index + 1} to peer {peer.get_peer_id()}')
                response = requests.get(peer_host, params=params) #send request and receive bianary data
                if response == 401:
                    while not block_queue.empty():
                        try:
                            block_queue.get_nowait()
                        except queue.Empty:
                            continue
                        block_queue.task_done()
                    break
                
                binary_data = response.content
                blocks_list[block_index] = binary_data
                block_queue.task_done()
                print (f'\n Downloaded block {block_index + 1}/ piece {piece_index + 1} from peer {peer.get_peer_id()} successfully.')
            except Exception as e:
                print(f'Error downloading block {block_index} from peer {peer}: {e}')
                block_queue.put(block_index)
        except queue.Empty:
            break  # No more blocks to download
    print ('\nThread finished')
    
        
def ask_user_to_connect_to_peers(peer_list, peers, needed_torrent):
    answer = input("Do you want to connect to other peers? (Y/N) \n")
    if (answer.lower() == 'y'): #if they want to connect to other peers
        for peer in peers:
            print('IP ', peer['ip'], ', Port: ', peer['port'])
            params = {
                'info_hash': peer['info_hash'],
                'peer_id': peer['peer_id'],
            }
            peer_host = 'http://' + peer['ip'] + ':' + str(peer['port'])
            response = requests.get(peer_host, params=params)
            
            if response.status_code == 200:
                print('Connect to peer', peer['peer_id'] , 'successfully.')
                # Todo
                bitfield = send_interested(peer_host, params['info_hash'])
                new_peer = Peer(peer['ip'], peer['port'], peer['peer_id'], needed_torrent, bitfield)
                peer_list.append(new_peer)
            else:
                print('Failed to send request.')
    elif (answer.lower() == 'n'):
        # Todo
        return

def ask_user_to_send_download_request(peer_list, pieces_list):
    print ("Starting download ...")
    piece_count = calculate_piece_count(peer_list)
    while piece_count:
        
        sorted_pieces = sorted(piece_count.items(), key=operator.itemgetter(1))
        rarest_piece = sorted_pieces[0][0]
        peers_with_piece = [peer for peer in peer_list if peer.get_bitfield()[rarest_piece] == '1']
        
        piece_length = peers_with_piece[0].get_torrent().get_piece_length()
        block_length = 16384 #16 KB
        num_blocks = math.ceil(piece_length/block_length)
        
        block_queue = queue.Queue()
        for block_index in range(num_blocks):
            block_queue.put(block_index)  # tao hang doi cho cac block
        
        print (f'\nNumber of blocks: {num_blocks}')
        print (f'\nNumber of elements in block queue: {block_queue.qsize()}')
        
        
        blocks_list = [None]*num_blocks # Create a list of blocks list to store downdloaded blocks from peers
        for index, peer in enumerate(peers_with_piece):
            print (f'{index}. Dowloading from peer {peer.get_peer_id()} ...')
            thread = threading.Thread(target=download_block, args=(peer, rarest_piece, block_length, block_queue, blocks_list))
            thread.start()
                    
        block_queue.join()
        
        complete_piece = b''.join(blocks_list)
        pieces_list[rarest_piece] = complete_piece
        piece_count.pop(rarest_piece)

    print (f'\nDownloaded all pieces successfully.')
    # peer_host = 'http://' + peer_list[1].get_ip() + ':' + str(peer_list[1].get_port()) + '/printfullfile'
    # response = requests.post(peer_host, data = json.dumps('hello'))

def ask_user_to_write_file (location, torrent):
    print ('\nWriting file ...')
    # print (f'All pieces: {torrent.get_pieces_list()}')
    existing_files = os.listdir(location[0])
    torrent_info = torrent.get_info()
    file_data = b''.join(torrent.get_pieces_list())
    data_offset = 0
    
    
    if 'files' in torrent.get_info(): #multiple files torrent
        for file_info in torrent_info['files']:
            file_path = os.path.join(location[0], file_info[b'path'][0].decode())
            if os.path.basename(file_path) not in existing_files:
                with open(file_path, 'wb') as f:
                    print(f'Created file {file_path}')
                    data = file_data[data_offset: data_offset + file_info[b'length']]
                    data_offset += file_info[b'length']
                    f.write(data)
                    print (f'Write data to file {file_path} successfully.')
            else:
                data_offset += file_info[b'length']
                print (f'File {file_path} already exists.')
    else: #single file only
        file_path = os.path.join(location[0], torrent_info['name'])
        if torrent_info['name'] not in existing_files:
            with open(file_path, 'wb') as f:
                data = file_data[data_offset: data_offset + torrent_info['length']]
                f.write(data)
                print (f'Write data to file {file_path} successfully.')
        else:
            print (f'File {file_path} already exists.')
            
    print ('\nWrite file successfully.')



    
    
# peer_list = []
# peer1 = Peer(1, 1, 1,1, '1001100')
# peer2 = Peer(1, 1, 1,1, '1001100')
# peer_list.append(peer1)
# peer_list.append(peer2)
# print (peer_list)
# piece_count = calculate_piece_count(peer_list)
# for piece, count in piece_count.items():
#     print(piece, count)
# sorted_pieces = sorted(piece_count.items(), key=operator.itemgetter(1))
# rarest_piece = sorted_pieces[0][0]
# print (rarest_piece)
# peers_with_piece = [peer for peer in peer_list if peer.get_bitfield()[rarest_piece] == '1']
# print (peers_with_piece)  
