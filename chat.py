import socket
import threading
import time
import argparse
import subprocess

class Client:
    def __init__(self, addr, port):
        self.client_socket = socket.socket()
        self.client_socket.connect((addr, port))
        self.running = True

    def handle_recieve_msg(self):
        while self.running:
            msg = self.client_socket.recv(1024).decode()
            print(msg)

    def handle_send_msg(self):
        while self.running:
            msg = input()
            if msg == "EXIT":
                self.client_socket.send(msg.encode())
                self.client_socket.close()
                self.stop()
            else:
                self.client_socket.send(msg.encode())

    def stop(self):
        exit()

    def run(self):
        threading.Thread(target=self.handle_recieve_msg, daemon=True).start()
        self.handle_send_msg()

class Server:
    HELP_MESSAGE = """
Available Commands:
    HELP           show this message
    EXIT           disconnect from the server
    TIME           get the current server time
    NAME <name>    set your name
    CMD <command>   run a shell command on the server
"""

    class Client:
        def __init__(self, socket) -> None:
            self.name = ""
            self.socket = socket

    def __init__(self, addr, port):
        self.running = False

        self.socket = socket.socket()
        self.socket.bind((addr, port))

        self.addr = addr
        self.port = port

        self.clients = [] # list of clients

    def accept_incomming_connections(self):
        while self.running:
            socket, _ = self.socket.accept()
            client = self.Client(socket)
            self.clients.append(client)
            print("Client connected")
            threading.Thread(
                target=self.handle_msg,
                args=(client,),
                daemon=True
            ).start()

    def set_client_name(self, client, name):
        for _client in self.clients:
            if client == _client:
                client.name = name
                return

    def unicast(self, msg, client):
        client.socket.send(msg.encode())

    def broadcast(self, msg, sender_client):
        _msg = ""
        if sender_client.name:
            _msg = f"{sender_client.name}: {msg}"
        else:
            _msg = msg

        if not sender_client:
            for client in self.clients:
                client.socket.send(_msg.encode())
        else:
            for client in self.clients:
                if client.socket != sender_client.socket:
                    client.socket.send(_msg.encode())

    def handle_msg(self, client):
        while self.running:
            msg = client.socket.recv(1024).decode()
            if msg:
                match msg:
                    case "EXIT":
                        self.clients.remove(client)
                        self.broadcast("Client disconnected", None)
                        print("Client disconnected")
                    case "HELP":
                        self.unicast(self.HELP_MESSAGE, client)
                    case msg if msg.startswith("NAME"):
                        name = msg.split(" ", 1)[1]
                        self.set_client_name(client, name)
                    case msg if msg.startswith("CMD"):
                        cmd = msg.split(" ")[1:]
                        output = subprocess.run(cmd, capture_output=True, text=True)
                        self.unicast(output.stdout, client)
                    case "TIME":
                        # TODO fix time format
                        current_time = time.localtime(time.time())
                        time_str = (
                            f"{current_time.tm_year}-{current_time.tm_mon}-"
                            f"{current_time.tm_mday}_{current_time.tm_hour}:"
                            f"{current_time.tm_min}"
                        )
                        self.unicast(f"Server time: {time_str}", client)
                    case _:
                        self.broadcast(msg, client)

    def run(self):
        self.running = True
        self.socket.listen()
        print(f"Serving on {self.addr}:{self.port}")

        self.accept_incomming_connections() # loops

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str)
    parser.add_argument("-a", "--address", type=str)
    parser.add_argument("-p", "--port", type=int)
    args = parser.parse_args()

    if args.type == "server":
        server = Server(args.address, args.port)
        server.run()
    elif args.type == "client":
        client = Client(args.address, args.port)
        client.run()
