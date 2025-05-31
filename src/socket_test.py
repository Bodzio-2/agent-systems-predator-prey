import socket
import json

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            # data = conn.recv(1024)
            # if not data:
            #     break

            r = {'name': 'Turbo cool name right?', 'count': 3.5}
            r = json.dumps(r)
            data = bytes(r, 'utf-8')
            conn.sendall(data)

            data = conn.recv(1024)

            if data:
                print(f"Received response: {data!r}")
            