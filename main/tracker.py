from flask import Flask, request

app = Flask(__name__)
swarm = []
    

def handle_request_event(peer_info, info_hash, peer_id, port, uploaded, downloaded, left, event):
    global swarm
    if event == "started":
        for existing_peer in swarm:
            if existing_peer['peer_id'] == peer_info['peer_id']:
                existing_peer.update(peer_info)
                return
        swarm.append(peer_info)
        return
    elif event == "stopped":
        swarm = [peer for peer in swarm if peer['peer_id'] != peer_id]
        return 
        
    elif event == "completed":
        return

        



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

    peer_info = {
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'uploaded': uploaded,
        'downloaded': downloaded,
        'left': left,
        'event': event
    }
    
    if event not in ['started', 'stopped', 'completed']:
        return 'Invalid event', 400
    handle_request_event(peer_info, info_hash, peer_id, port, uploaded, downloaded, left, event)

    print (swarm)






    return 'Peer added to swarm successfully.', 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1234)
