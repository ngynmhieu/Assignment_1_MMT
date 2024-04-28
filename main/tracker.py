import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

class Peer_in_track:
    def __init__(self, ip, info_hash, peer_id, port, uploaded, downloaded, left, event):
        self.ip = ip
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port
        self.uploaded = uploaded
        self.downloaded = downloaded
        self.left = left
        self.event = event
        self.last_contact = time.time()
    
    def get_ip(self):
        return self.ip
    def get_info_hash(self):
        return self.info_hash
    def get_peer_id(self):
        return self.peer_id
    def get_port(self):
        return self.port
    def get_uploaded(self):
        return self.uploaded
    def get_downloaded(self):
        return self.downloaded
    def get_left(self):
        return self.left
    def get_event(self):
        return self.event
    def get_last_contact(self):
        return self.last_contact
    def update_last_contact(self):
        self.last_contact = time.time() #in ra thoi gian bay gio - ngay 1/1/1970 ?? ra so giay
    def update (self, new_peer):
        self.uploaded = new_peer.get_uploaded()
        self.downloaded = new_peer.get_downloaded()
        self.left = new_peer.get_left()
        self.event = new_peer.get_event()
        self.last_contact = time.time()
swarm = []
    
def handle_request_event(peer):
    global swarm
    if peer.get_event() == "started":
        for existing_peer in swarm:
            if existing_peer.get_peer_id() == peer.get_peer_id() and existing_peer.get_info_hash() == peer.get_info_hash():
                existing_peer.update(peer)
                return
        swarm.append(peer)
        return
    elif peer.get_event() == "stopped":
        swarm = [existing_peer for existing_peer in swarm if existing_peer.get_peer_id() != peer.get_peer_id()]
        return 
    elif peer.get_event() == "completed":
        # Update the peer status to completed
        for existing_peer in swarm:
            if existing_peer.get_peer_id() == peer.get_peer_id() and existing_peer.get_info_hash() == peer.get_info_hash():
                existing_peer.update(peer)
        return

def check_peer_status():
    global swarm
    while True:
        current_time = time.time()
        swarm = [peer for peer in swarm if current_time - peer.get_last_contact() <= 120] #2minute
        time.sleep(60) #1 minute


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
        'ip': request.remote_addr,
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'uploaded': uploaded,
        'downloaded': downloaded,
        'left': left,
        'event': event
    }
    temp_peer = Peer_in_track(peer_info['ip'], peer_info['info_hash'], peer_info['peer_id'], 
                              peer_info['port'], peer_info['uploaded'], peer_info['downloaded'], 
                              peer_info['left'], peer_info['event'])
    if event not in ['started', 'stopped', 'completed']:
        return 'Invalid event', 400
    
    
    handle_request_event(temp_peer)

    print (swarm)
    print ('\n --------------------------------- \n')
    if int(left) > 0:
        peers_dict = []
        for peer in swarm:
            
            if int (peer.get_left()) == 0 and peer.get_info_hash() == info_hash:
                peers_dict.append({
                    'peer_id': peer.get_peer_id(),
                    'ip': peer.get_ip(),
                    'port': peer.get_port()
                })
            
        response = {
            'failure_reason': 'No failure reason',
            'tracker_id': '1234',
            'ready_peers_list': peers_dict
            
        }
        return response, 200

    return 'Peer added to swarm successfully.', 200

if __name__ == '__main__':
    
    # Thread checking peer status every 1 minutes
    check_peer_status = threading.Thread (target = check_peer_status)
    check_peer_status.start()
    
    app.run(host='127.0.0.1', port=1234)
