from connection import *
from torrent import *



torrent = read_torrent_file('C:/Users/Minh Hieu/OneDrive/Desktop/MMT_A1/Assignment_1_MMT/main/testing/test.torrent')
info_hash = torrent2hash(torrent.get_info())


send_request_to_tracker('127.0.0.1', info_hash, '1', 1234, 0,0,0,'started')

# from flask import Flask, request

# app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def handle_request():
#     params = request.args.to_dict()

#     # Xử lý yêu cầu ở đây

#     return params  # Trả về phản hồi
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=1234)