from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def handle_request():
    params = request.args.to_dict()
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    port = request.args.get('port')
    uploaded = request.args.get('uploaded')
    downloaded = request.args.get('downloaded')
    left = request.args.get('left')
    event = request.args.get('event')

    # Xử lý yêu cầu tại đây...
    # ...
    print(f'Info hash: {info_hash}')
    print(f'Peer ID: {peer_id}')
    print(f'Port: {port}')
    print(f'Uploaded: {uploaded}')
    print(f'Downloaded: {downloaded}')
    print(f'Left: {left}')
    print(f'Event: {event}')


    return params

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1234)
