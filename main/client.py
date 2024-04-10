import sys
from torrent import *
import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify
import json
from threading import Thread


PORT = 9999
TRACKER_PORT = 1234

app = Flask(__name__)


def send_request_to_tracker(tracker_host, trasker_port, info_hash, peer_id, port, uploaded, downloaded, left, event):
    params = {
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'uploaded': uploaded,
        'downloaded': downloaded,
        'left': left,
        'event': event
    }
    tracker_host = 'http://' + tracker_host + ':' + str(trasker_port)
    response = requests.get(tracker_host, params=params)
    
    if response.status_code == 200:
        print('Request sent successfully.')
        try:
            # Phân tích cú pháp đối tượng JSON trong phản hồi
            response_json = json.loads(response.text)
            # Lấy và in danh sách peers
            peers = response_json.get('peers', [])
            print('Received list of peers:', peers)
            return peers
        except json.JSONDecodeError:
            print('Failed to parse response as JSON or no json file')
            return
    else:
        print('Failed to send request.')

def start_flask_app():
    app.run(host='127.0.0.1', port=9000)

def ask_user_to_connect_to_peers(peers):
    answer = input("Do you want to connect to other peers? (Y/N) \n")
    if (answer.lower() == 'y'):
        for peer in peers:
            print('IP ', peer['ip'], ', Port: ', peer['port'])
        
        
        return
    elif (answer.lower() == 'n'):
        # Todo
        
        return

def ask_user_to_import_torrent_file():
    while True:
        answer = input("Do you want to send request to tracker? (Y/N) \n")
        if (answer.lower() == 'y'):
            filepath = import_file()
            
            torrent = read_torrent_file(filepath)
            info_hash = torrent2hash(torrent.get_info())
            tracker_host = torrent.get_announce()
            tracker_port = TRACKER_PORT
            port = PORT
            peers = send_request_to_tracker(tracker_host, tracker_port, info_hash, '3', port, 0, 0, 90, 'started')
            if peers: 
                ask_user_to_connect_to_peers(peers)
            else:
                print ("No peers to connect to. Try again.")
        elif (answer.lower() == 'exit'):
            print("Existing ... ")
            sys.exit(0)

        
        
@app.route('/', methods=['GET'])
def handle_request():
    # Lấy thông tin từ yêu cầu
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    port = request.args.get('port')
    uploaded = request.args.get('uploaded')
    downloaded = request.args.get('downloaded')
    left = request.args.get('left')
    event = request.args.get('event')

    # Xử lý yêu cầu tại đây

    return 'Peer received request.', 200



if __name__ == '__main__':
    #Thread listening 
    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()

    #THREAD IMPORT AND RUN FILE
    ask_user_to_import_torrent_file()
    