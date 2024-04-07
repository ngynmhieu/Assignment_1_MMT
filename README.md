# Assignment_1_MMT

**3 file trước mắt:**
- torrent.py: bao gồm các hàm liên quan đến việc xử lý file torrent (Updating)
- tracker.py: tiếp nhận request từ client (sau khi client chạy torrent) và gửi danh sách các máy peer cho client đó (Updating)
- peer.py: bao gồm dowloading và uploading, sau khi nhận danh sách các peer thì sẽ thực hiện kết nối và trao đổi dữ liệu, uploading thì sau khi tải xong tệp thì sẽ đóng vai trò là một seeder của file vừa tải (Updating)


**Dowloading**
- trường piece trong file torrent giúp đảm bảm khi tải, các mảnh được tải về sẽ trùng khớp với mã hash trong piece

 ## Connection.py
 ### send_request_to_tracker(): Dùng để gửi request từ máy peer sang tracker
 - tracker_host: địa chỉ ip của tracker (trong máy local thì là "127.0.0.1")
 - info_hash: dùng hàm torrent_to_hash để chuyển đổi file torrent thành mã hash tương ứng (torrent2hash, cần phải lấy info của torrent bằng hàm read_torrent_file mới sử dụng được hàm torrent2hash)
 - peer_id: tự chọn
 - port: quy định là 1234
 - uploaded: máy peer đã upload được bao nhiêu byte
 - dowloaded: máy peer đã dowload được bao nhiêu byte, nếu chưa đủ 100% thì tiến hành dowload tiếp
 - left: lượng byte còn thiếu
 - event: gồm 3 phần (started, stopped và completed). Started thì bắt đầu tải, stopped thì dừng tải, completed thì tải xong thì báo
 ## Torrent.py

 ## Tracker.py

 ## Peer.py

**Uploading (Peer)** 
- Gửi request start tới tracker thông qua hàm peer2trackerRqstarted
- Sau khi kết nối với tracker thành công thì máy peer chế độ chờ request từ máy client
- Khi máy client gửi request cho các máy peer khác, máy peer sẽ tự tìm tài liệu được yêu cầu trong máy đó để tiến hành upload cho 
máy client
**Dowloading (Client)**
- Gửi request tới tracker thông tin file muốn tải thông qua hàm peer2trackerRq
- Nếu muốn dừng thì dùng request stopped
- Nếu tải xong thì dùng request completed
- Sau khi nhận được list các peer sở hữu file đó, tiến hành gửi request tới các peer đó yêu cầu dowload
- Nếu dowload thành công sẽ tự động trở thành máy peer dạng uploading như trên
