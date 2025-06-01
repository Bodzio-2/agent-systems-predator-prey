import socket

HOST = "127.0.0.1"
PORT = 65432

class UnityConnection:
    def __init__(self):
        print(f"Starting connection {HOST}:{PORT}...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen()

        self.conn, self.addr = self.s.accept()
        print("Connected!")

    
    def send_data(self, data: str):
        data = bytes(data, 'utf-8')
        self.conn.sendall(data)

        data = self.conn.recv(1024)

        if data:
            print("Data sent successfully!")


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()

#     conn, addr = s.accept()
#     with conn:
#         print(f"Connected by {addr}")
#         while True:
#             # data = conn.recv(1024)
#             # if not data:
#             #     break

#             r = {'name': 'Turbo cool name right?', 'count': 3.5}
#             r = json.dumps(r)
#             data = bytes(r, 'utf-8')
#             conn.sendall(data)

#             data = conn.recv(1024)

#             if data:
#                 print(f"Received response: {data!r}")
            