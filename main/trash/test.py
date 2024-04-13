import hashlib

def create_pieces(data, piece_length):
    pieces = []
    hashes = []
    for i in range(0, len(data), piece_length):
        piece = data[i:i+piece_length]
        pieces.append(piece)
        piece_hash = hashlib.sha1(piece).digest()
        hashes.append(piece_hash)
    return pieces, hashes

def verify_piece(piece, piece_hash):
    """Kiểm tra tính toàn vẹn của một piece bằng cách so sánh mã hash."""
    return hashlib.sha1(piece).digest() == piece_hash

# Tạo dữ liệu mẫu
data = b"This is some example data for a torrent file."

# Chia dữ liệu thành các pieces và tạo mã hash
pieces, hashes = create_pieces(data, 10)

# Kiểm tra tính toàn vẹn của một piece
for counter in range(len(pieces) - 1):
    print (pieces[counter], hashes[counter])