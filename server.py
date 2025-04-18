"""Main server file for the chat application."""
import socket
import threading

from utils import get_key, generate_key
from hashlib import sha256


class Server:
    """Class for the chat server."""
    def __init__(self, port: int) -> None:
        self.host = '127.0.0.1'
        self.port = port
        self.clients = []
        self.client_keys = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def start(self):
        """Method to start the server."""
        self.s.bind((self.host, self.port))
        self.s.listen(100)

        p, q = get_key(), get_key()
        self.mod = p * q
        phi = (p - 1) * (q - 1)

        self.encrypt_key = generate_key(phi) # public key for the server
        self.decrypt_key = pow(self.encrypt_key, -1, phi) # private key for the server

        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.clients.append(c)

            client_key = int.from_bytes(c.recv(128))
            client_mod = int.from_bytes(c.recv(128))

            self.client_keys[c] = (client_key, client_mod)

            c.send(self.encrypt_key.to_bytes(128))
            c.send(self.mod.to_bytes(128))

            self.broadcast(f'new person has joined: {username}')

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    def broadcast(self, msg: str):
        """Method to broadcast a message to all clients."""
        for client in self.clients:
            cipher = ''
            for char in msg:
                cipher += f'{ord(char):03}'
            cipher = int(cipher)

            client_key, client_mod = self.client_keys[client]
            hashed = sha256(str(cipher).encode())

            crypted_msg = pow(cipher, client_key, client_mod)
            client.send(crypted_msg.to_bytes(1024))
            client.send(int(hashed.hexdigest(), 16).to_bytes(128))

    def handle_client(self, c: socket, addr):
        """Method to handle incoming messages from a client."""
        while True:
            msg = int.from_bytes(c.recv(1024))
            hashed = c.recv(128)
            crypted = int(msg)
            decrypted = pow(crypted, int(self.decrypt_key), int(self.mod))

            for client in self.clients:
                if client != c:
                    client_key, client_mod = self.client_keys[client]
                    crypted_msg = pow(int(decrypted), client_key, client_mod)
                    client.send(crypted_msg.to_bytes(1024))
                    client.send(hashed)

if __name__ == "__main__":
    s = Server(9001)
    s.start()
