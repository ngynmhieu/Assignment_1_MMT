import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify
import json
import hashlib
#tracker connection
# class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # def do_GET(self):
    #     self.send_response(200)
    #     self.end_headers()
    #     self.wfile.write(b'Handled GET request\n')
    #     print(f"Path: {self.path}")
    #     print(f"Headers: {self.headers}")

# def start_tracker_server(tracker_host, tracker_port):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     sock.bind((tracker_host, tracker_port))
    #     sock.listen()

    #     print(f"Tracker is running at {tracker_host}:{tracker_port}")

    #     while True:
    #         conn, addr = sock.accept()
    #         print(f"Connected with {addr[0]}:{addr[1]}")
            
    #         request = conn.recv(1024).decode('utf-8')
    #         request_line, headers_alone = request.split('\r\n', 1)
    #         headers = SimpleHTTPRequestHandler.parse_headers(BytesIO(headers_alone.encode('iso-8859-1')))
    #         handler = SimpleHTTPRequestHandler(request_line, None, conn, headers=headers)
    #         handler.do_GET()
            
    # except socket.error as e:
    #     print(f"Cannot start tracker server: {e}")
    # finally:
    #     sock.close()

#peer connection
# def connect_to_tracker(tracker_host, tracker_port):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # try:
    #     sock.connect((tracker_host, tracker_port))
    #     print(f"Connected with tracker at {tracker_host}:{tracker_port}")
    #     return sock
    # except socket.error as e:
    #     print(f"Cannot connect to tracker at {e}")
    #     return None


# Send request to tracker
# def peer2trackerRq(sock, tracker_host, tracker_port, info_hash, peer_id):
    # if sock is None:
    #     print ("No connection to tracker.")
    #     return
    # try:
    #     sock.connect((tracker_host, tracker_port))
    #     print(f"Connected with tracker at {tracker_host}:{tracker_port}")

    #     params = urllib.parse.urlencode({'info_hash': info_hash, 
    #                                      'peer_id': peer_id, 'port': 1234, 
    #                                      'uploaded': 0, 'downloaded': 0, 
    #                                      'left': 0, 'event': 'started'})
    #     request = f"GET /announce?{params} HTTP/1.1\r\nHost: {tracker_host}:{tracker_port}\r\nConnection: close\r\n\r\n"

    #     sock.send(request.encode())

    #     response = sock.recv(1024)
    #     print(f"Received response from tracker: {response}")

    # except socket.error as e:
    #     print(f"Cannot connect to tracker: {e}")
    # finally:
    #     sock.close()

# PEER SIDE
def hash_to_metainfo(hex_hash):
    # Convert the hexadecimal hash to a binary hash
    binary_hash = bytes.fromhex(hex_hash)

    # The metainfo file structure
    metainfo = {
        'announce': 'http://tracker.example.com/announce',
        'info': {
            'files': [
                {'length': 111, 'path': ['111.txt']},
                {'length': 222, 'path': ['222.txt']}
            ],
            'name': 'directoryName',
            'piece length': 262144,
            'pieces': '<binary SHA1 hashes>'
        }
    }

    # Replace placeholder with actual binary hashes
    metainfo['info']['pieces'] = binary_hash

    # Convert the metainfo to a JSON string
    metainfo_json = json.dumps(metainfo, indent=4)

    return metainfo_json
        
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
        except json.JSONDecodeError:
            print('Failed to parse response as JSON or no json file')
    else:
        print('Failed to send request.')

