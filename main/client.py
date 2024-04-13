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
PEER_ID = 9

# global var
torrents=[] # List of torrents and info hash in this system
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

def ask_user_to_connect_to_peers(peers):
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
            else:
                print('Failed to send request.')
    elif (answer.lower() == 'n'):
        # Todo
        return

        
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
                                ask_user_to_connect_to_peers(peers)
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


if __name__ == '__main__':
    #Thread listening 
    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()

    #THREAD IMPORT AND RUN FILE
    ask_user_to_choose_location()
    ask_user()
    