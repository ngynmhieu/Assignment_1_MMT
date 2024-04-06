# Assignment_1_MMT

**3 file trước mắt:**
- torrent.py: bao gồm các hàm liên quan đến việc xử lý file torrent (Updating)
- tracker.py: tiếp nhận request từ client (sau khi client chạy torrent) và gửi danh sách các máy peer cho client đó (Updating)
- peer.py: bao gồm dowloading và uploading, sau khi nhận danh sách các peer thì sẽ thực hiện kết nối và trao đổi dữ liệu, uploading thì sau khi tải xong tệp thì sẽ đóng vai trò là một seeder của file vừa tải (Updating)


**Dowloading**
- trường piece trong file torrent giúp đảm bảm khi tải, các mảnh được tải về sẽ trùng khớp với mã hash trong piece