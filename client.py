import socket
import threading

class Client:
    def __init__(self, addr, port):
        self.client_socket = socket.socket()
        self.client_socket.connect((addr, port))
        self.running = True

    def handle_recieve_msg(self):
        while self.running:
            msg = self.client_socket.recv(1024).decode()
            print(self.client_socket, msg)

    def handle_send_msg(self):
        while self.running:
            msg = input()
            self.client_socket.send(msg.encode())

    def run(self):
        threading.Thread(target=self.handle_recieve_msg, daemon=True).start()
        self.handle_send_msg()

client = Client("localhost", 9997)
client.run()
