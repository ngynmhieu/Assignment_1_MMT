from flask import Flask, request, jsonify, send_file
import binascii
import urllib

app = Flask(__name__)

# This will store the peer info in memory
torrent_peers = {}

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            return(contents)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IOError:
        print(f"Error reading file: {file_path}")

def download_file(filename):
    # This is a very basic example. In a real application, you would need to
    # secure this to prevent unauthorized access and directory traversal attacks.

    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404
@app.route('/announce', methods=['GET'])
def announce():
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    ip = request.args.get('ip') or request.remote_addr
    port = request.args.get('port', type=int)

    if not all([info_hash, peer_id, ip, port]):
        return jsonify({'error': 'Missing required parameters'}), 400

    readable_info_hash = binascii.hexlify(urllib.parse.unquote_to_bytes(info_hash)).decode()
    filename = request.args.get('filename')

    peers = torrent_peers.setdefault(readable_info_hash, {})
    peers[peer_id] = {'ip': ip, 'port': port}

    print(f"Tracked Peers for {readable_info_hash}: {peers}")

    response_peers = [details for pid, details in peers.items() if pid != peer_id]

    return read_file(filename)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
