import socket

def connect_to_tracker(tracker_host, tracker_port):
    # Tạo một socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Kết nối đến tracker
        sock.connect((tracker_host, tracker_port))
        print(f"Đã kết nối đến tracker tại {tracker_host}:{tracker_port}")
    except socket.error as e:
        print(f"Không thể kết nối đến tracker: {e}")
    finally:
        # Đảm bảo rằng socket luôn được đóng lại sau khi sử dụng
        sock.close()

# Thông tin về tracker
tracker_host = "127.0.0.1"  # Địa chỉ IP cục bộ
tracker_port = 1234  # Port mặc định của BitTorrent

# Kết nối đến tracker
connect_to_tracker(tracker_host, tracker_port)