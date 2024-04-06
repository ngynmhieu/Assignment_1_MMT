
from connection import *

sock = connect_to_tracker("127.0.0.1", 1234)
send_tracker_request (sock,"127.0.0.1", 1234,)