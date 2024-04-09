from connection import *
from torrent import *
import socket
import urllib.parse
import requests
from flask import Flask, request, jsonify
import json

def send_request_to_tracker(tracker_host, info_hash, peer_id, port, uploaded, downloaded, left, event):
    params = {
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'uploaded': uploaded,
        'downloaded': downloaded,
        'left': left,
        'event': event
    }
    tracker_host = 'http://' + tracker_host + ':' + str(port)
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



torrent = read_torrent_file('C:/Users/Minh Hieu/OneDrive/Desktop/MMT_A1/Assignment_1_MMT/main/testing/test.torrent')
info_hash = torrent2hash(torrent.get_info())


send_request_to_tracker('127.0.0.1', info_hash, '1', 1234,0,0,90,'started')
