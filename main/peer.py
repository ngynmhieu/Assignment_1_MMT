# peer.py
import bencode
import requests
import hashlib
import urllib.parse
import socket
import os

def read_torrent_file(file_path):
    with open(file_path, 'rb') as file:
        torrent_data = file.read()
    return bencode.bdecode(torrent_data)

def announce_to_tracker(metainfo, peer_id, port):
    tracker_url = metainfo['announce']
    info_hash = hashlib.sha1(bencode.bencode(metainfo['info'])).digest()
    filename = metainfo['info'].get('name', 'unknown')
    params = {
        'info_hash': urllib.parse.quote(info_hash),
        'peer_id': peer_id,
        'port': port,
        'uploaded': 0,
        'downloaded': 0,
        'left': metainfo['info']['length'],
        'compact': 1,
        'filename': filename
    }
    print(filename)
    response = requests.get(tracker_url, params=params)
    if response.ok:
        print("Announce successful. Response from tracker:", response.text)
    else:
        print("Failed to announce to the tracker. Status code:", response.status_code)

# Example usage
torrent_file_path = 'yourfile.torrent'  # Path to your torrent file
metainfo = read_torrent_file(torrent_file_path)
peer_id = '-PY0001-' + os.urandom(12).hex()          # Randomly generated peer ID
port = 6881                                          # Port number

announce_to_tracker(metainfo, peer_id, port)
