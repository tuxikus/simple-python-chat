import socket
import threading

class Server:
    def __init__(self, addr, port):
        self.server_socket = socket.socket()
        self.server_socket.bind((addr, port))
        self.running = False
        self.client_socket = None

    def handle_recieve_msg(self, client):
        while self.running:
            msg = client.recv(1024).decode()
            print(client, msg)

    def handle_send_msg(self, client):
        while self.running:
            msg = input()
            client.send(msg.encode())

    def run(self):
        self.server_socket.listen()
        print("Waiting for connection")

        client, addr = self.server_socket.accept()
        print(addr, "connected")

        self.running = True

        threading.Thread(target=self.handle_recieve_msg, args=(client,), daemon=True).start()
        self.handle_send_msg(client)

server = Server("localhost", 9997)
server.run()
