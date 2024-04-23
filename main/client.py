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

PORT = 9999
TRACKER_PORT = 1234
PEER_ID = 9

# global var
torrents=[] # List of torrents and info hash in this system
dowload_requests = [] # List of download requests
location = []
app = Flask(__name__)

def ask_user_to_choose_location():
    root = Tk()
    root.after(0, lambda: open_directory(root, location))
    root.mainloop()
    if location:  # Check if the list is not empty
        return location
    else:
        print("No directory selected.")
        return None

def send_request_to_tracker(torrent, event):
    tracker_host = torrent.get_announce()
    tracker_port = TRACKER_PORT
    port = PORT
    peer_id = PEER_ID
    left = torrent.get_left()
    info_hash = torrent.get_info_hash()
    uploaded = torrent.get_uploaded()
    downloaded = torrent.get_dowloaded()
    
    
    params = {
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'uploaded': uploaded,
        'downloaded': downloaded,
        'left': left,
        'event': event
    }
    tracker_host = 'http://' + tracker_host + ':' + str(tracker_port)
    response = requests.get(tracker_host, params=params)
    
    if response.status_code == 200:
        print('Request sent successfully.')
        try:
            response_json = json.loads(response.text)
            peers = response_json.get('peers', [])
            print('Received list of peers:', peers)

            return peers
        except json.JSONDecodeError:
            print('No json file needed to return')
            return
    else:
        print('Failed to send request.')

def start_flask_app():
    app.run(host='127.0.0.1', port=PORT)
        
def ask_user():
    
    while True:
        print ('\n -------------------------------------------- \n')
        answer = input("Which action do you want: Import(I)/ Run(R)\n")
        if (answer.lower() == 'i'):
            filepath = import_file()
            torrent = read_torrent_file(filepath)
            info_hash = torrent2hash(torrent.get_info())
            torrent.set_info_hash(info_hash)
            verify_data_left(location, torrent)
            print (f'Pieces list {torrent.get_pieces_list()}')
            torrents.append((torrent)) #save torrent into torrents list
        elif (answer.lower() == 'r'):
            while True:
                if torrents: 
                    count = 1
                    for torrent in torrents:
                        print('Torrent', count, torrent.get_name())
                        count += 1
                    answer = input("Which torrent file you want to run or Exit (e) ?\n")
                    if answer.isdigit():
                        index = int (answer)
                        if (index < 1 or index > count):
                            print ('Wrong input, please try again')
                            continue
                        else:  
                            needed_torrent = torrents[index - 1]
                            peers = send_request_to_tracker(needed_torrent, 'started')
                            if peers:
                                peer_list = []
                                ask_user_to_connect_to_peers(peer_list, peers, needed_torrent)# lay list cac peer 
                                ask_user_to_send_download_request(peer_list, needed_torrent.get_pieces_list())
                                ask_user_to_write_file(location, needed_torrent)
                            else:
                                print ('No peers to connect to. Try again')
                                break
                    elif (answer.lower() == 'e'):
                        break
                    
                else: # No torrent file in the system
                    print ('No torrents in the system')
                    break
        elif (answer.lower() == 'exit'):
            print ("Existing ... ")
            sys.exit(0)

@app.route('/', methods=['GET'])
def handle_request():
    # Lấy thông tin từ yêu cầu
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')

    for torrent in torrents:
        if torrent.get_info_hash() == info_hash and int(peer_id) == PEER_ID:
            #todo 
            return 'Peer received message from Client', 200

    return 'Invalid info_hash or peer_id', 400


@app.route ('/', methods = ['POST'])
def handle_post_request():
    request_data = json.loads(request.data)
    if request_data['message'] == 'INTERESTED':
        # Todo
        for torrent in torrents:
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
    for torrent in torrents:
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
    ask_user_to_choose_location()
    ask_user()
    