"""Module for the client side of the chat application using RSA encryption."""
import socket
import threading

from utils import get_key, generate_key
from hashlib import sha256


class Client:
    """Client class for the chat application."""
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username
        self.running = True

    def init_connection(self):
        """Method to initialize the connection to the server."""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        # create key pairs(prime numbers)
        p, q = get_key(), get_key()
        self.mod = p * q
        phi = (p - 1) * (q - 1)

        encrypt_key = generate_key(phi)
        self.decrypt_key = pow(encrypt_key, -1, phi)

        # exchange public keys
        self.s.send(encrypt_key.to_bytes(128))
        self.s.send(self.mod.to_bytes(128))

        # receive the encrypted secret key
        self.server_key = int.from_bytes(self.s.recv(128))
        self.server_mod = int.from_bytes(self.s.recv(128))

        message_handler = threading.Thread(target=self.read_handler,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler,args=())
        input_handler.start()

    def read_handler(self):
        """Method to handle incoming messages from the server."""
        while self.running:
            if not self.s:
                break

            message = int.from_bytes(self.s.recv(1024))
            hashed = int.from_bytes(self.s.recv(128))

            decrypted = str(pow(int(message), int(self.decrypt_key), int(self.mod)))

            if len(decrypted) % 3 != 0:
                decrypted = '0' + decrypted

            curr_hashed = sha256(decrypted.encode())
            if int(curr_hashed.hexdigest(), 16) != hashed:
                raise ValueError('The message was damaged.')

            message = ''
            for i in range(0, len(decrypted), 3):
                message += chr(int(decrypted[i:i + 3]))

            print(message)

    def write_handler(self):
        """Method to handle sending messages to the server."""
        while self.running:
            message = input()
            cipher = ''
            if message == 'q':
                message = f'{self.username} has left the chat'
                for char in message:
                    cipher += f'{ord(char):03}'

                hashed = sha256(cipher.encode())

                crypted_msg = pow(int(cipher), int(self.server_key), int(self.server_mod))
                self.s.send(crypted_msg.to_bytes(1024))
                self.s.send(int(hashed.hexdigest(), 16).to_bytes(128))
                print("You have left the chat")
                self.running = False
                break

            message = f'{self.username}: {message}'

            for char in message:
                cipher += f'{ord(char):03}'

            hashed = sha256(cipher.encode())

            crypted_msg = pow(int(cipher), int(self.server_key), int(self.server_mod))
            self.s.send(crypted_msg.to_bytes(1024))
            self.s.send(int(hashed.hexdigest(), 16).to_bytes(128))


if __name__ == "__main__":
    name = input("Please enter you username: ")
    cl = Client("127.0.0.1", 9001, name)
    cl.init_connection()
