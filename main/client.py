import sys
from torrent import *
import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify, send_file
from io import BytesIO
import json
from threading import Thread
from peer_func import *

PORT = 9000
TRACKER_PORT = 1234
PEER_ID = 9

# global var
torrent_list=[] # List of torrents and info hash in this system
location = []

app = Flask(__name__)

# ----------------------LISTENING TO PEER REQUESTS----------------------
def start_flask_app():
    app.run(host='127.0.0.1', port=PORT)
    
@app.route('/', methods=['GET'])
def handle_request():
    # Lấy thông tin từ yêu cầu
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')

    for torrent in torrent_list:
        if torrent.get_info_hash() == info_hash and int(peer_id) == PEER_ID:
            #todo 
            return 'Peer received message from Client', 200

    return 'Invalid info_hash or peer_id', 400

@app.route ('/', methods = ['POST'])
def handle_post_request():
    request_data = json.loads(request.data)
    if request_data['message'] == 'INTERESTED':
        # Todo
        for torrent in torrent_list:
            if torrent.get_info_hash() == request_data['info_hash']:
                bitfield = generate_bitfield(location, torrent, torrent.get_pieces_list(), torrent.get_hash_pieces_list())
                print ("Client ask interested and bitfield is: ", bitfield)
                response = {'bitfield': bitfield}
                return json.dumps(response),200
    return 'Invalid request', 400

@app.route('/download', methods=['GET'])
def handle_download_request():
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    piece_index = request.args.get('piece_index')
    block_index = int(request.args.get('block_index'))
    block_length = request.args.get('block_length')

    #lay duoc piece giong voi piece index
    needed_torrent = None
    print (f'Info hash {info_hash}')
    for torrent in torrent_list:
        if torrent.get_info_hash() == info_hash:
            needed_torrent = torrent
            break
    pieces_list = needed_torrent.get_pieces_list()
    required_piece = pieces_list[int(piece_index)]
    #lay duoc block giong voi block index
    blocks = [required_piece[i:i+int(block_length)] for i in range(0, len(required_piece), int(block_length))]
    print (f'Blocks number = {len(blocks)}')
    if block_index >= len(blocks):
        return 'Block index out of range', 401
    required_block = blocks[int(block_index)]
    if not isinstance(required_block, bytes):
        required_block = bytes(required_block, 'utf-8')

    # Create a BytesIO object from your data
    data = BytesIO(required_block)
    # Send data as a file
    return send_file(data, mimetype='application/octet-stream')

# @app.route('/printfullfile', methods=['POST'])
# def handle_printfullfile_request():
#     print (f'Print full file: {torrents[0].get_pieces_list()}')
#     return 'Print full file', 200

if __name__ == '__main__':
    #Thread listening 
    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()

    #THREAD IMPORT AND RUN FILE
    ask_user_to_choose_location(location)
    ask_user(PORT, TRACKER_PORT, PEER_ID, location, torrent_list)
    