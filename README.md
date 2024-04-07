# Assignment_1_MMT


 ## Connection.py
 ### send_request_to_tracker(): Dùng để gửi request từ máy peer sang tracker
 - tracker_host: địa chỉ ip của tracker (trong máy local thì là "127.0.0.1")
 - info_hash: dùng hàm torrent_to_hash để chuyển đổi file torrent thành mã hash tương ứng (torrent2hash, cần phải lấy info của torrent bằng hàm read_torrent_file mới sử dụng được hàm torrent2hash)
 - peer_id: tự chọn
 - port: quy định là 1234
 - uploaded: máy peer đã upload được bao nhiêu byte
 - dowloaded: máy peer đã dowload được bao nhiêu byte, nếu chưa đủ 100% thì tiến hành dowload tiếp
 - left: lượng byte còn thiếu (nếu byte = 0 thì tracker không cần gửi text/plain cho máy peer nữa và xem máy peer là seeder, > 0 thì xem là leecher)
 - event: gồm 3 phần (started, stopped và completed). Started thì bắt đầu tải, stopped thì dừng tải, completed thì tải xong thì báo
 ## Torrent.py

 ## Tracker.py
 ### handler_request_event(): Dung de xử lý các tín hiệu event khác nhau:
 - started: add thông tin peer_info vào swarm hoặc update
 - stopped: xóa thông tin peer_info ra khỏi swarm
 - completed: chưa biết làm gì (Updating)
 ### handle_request(): Dùng để xử lý các yêu cầu get được gửi tới
 - array swarm[] dùng để lưu trữ thông tin các peer gửi request tới, khi một peer yêu cầu dowload thì sẽ gửi danh sách các peer chứa file yêu cầu cho client đó
 ## Peer.py

### Uploading (Peer)
- Gửi request start tới tracker thông qua hàm send_request_to_tracker
- Sau khi kết nối với tracker thành công thì máy peer chế độ chờ request từ máy client
- Khi máy client gửi request cho các máy peer khác, máy peer sẽ tự tìm tài liệu được yêu cầu trong máy đó để tiến hành upload cho 
máy client
### Dowloading (Client)
- Gửi request tới tracker thông tin file muốn tải thông qua hàm send_request_to_tracker
- Sau khi nhận được list các peer sở hữu file đó, tiến hành gửi request tới các peer đó yêu cầu dowload
- Nếu dowload thành công sẽ tự động trở thành máy peer dạng uploading như trên
