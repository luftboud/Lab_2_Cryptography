"""Module for the client side of the chat application using RSA encryption."""
import socket
import threading

from utils import get_key, generate_key

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

            message = self.s.recv(1024).decode()

            decrypted = str(pow(int(message), int(self.decrypt_key), int(self.mod)))

            if len(decrypted) % 3 != 0:
                decrypted = '0' + decrypted

            message = ''
            for i in range(0, len(decrypted), 3):
                message += chr(int(decrypted[i:i + 3]))

            print(message)

    def write_handler(self):
        """Method to handle sending messages to the server."""
        while self.running:
            message = input()
            if message == 'q':
                message = f'{self.username} has left the chat'
                cipher = ''
                for char in message:
                    cipher += f'{ord(char):03}'

                crypted_msg = pow(int(cipher), int(self.server_key), int(self.server_mod))
                self.s.send(str(crypted_msg).encode())
                print("You have left the chat")
                self.running = False
                break

            message = f'{self.username}: {message}'

            cipher = ''
            for char in message:
                cipher += f'{ord(char):03}'

            crypted_msg = pow(int(cipher), int(self.server_key), int(self.server_mod))
            self.s.send(str(crypted_msg).encode())


if __name__ == "__main__":
    name = input("Please enter you username: ")
    cl = Client("127.0.0.1", 9001, name)
    cl.init_connection()
