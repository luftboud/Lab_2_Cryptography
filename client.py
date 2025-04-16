import socket
import threading

import random
from math import gcd


class Client:
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username

    @staticmethod
    def miller_rabin(n, k=100):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False

        r, d = 0, n - 1
        while d % 2 == 0:
            d //= 2
            r += 1

        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True

    @staticmethod
    def get_key():
        num = random.randint(10 ** 100, 10 ** 101)
        while True:
            if Client.miller_rabin(num):
                return num

            num += 1

    @staticmethod
    def generate_key(phi):
        for i in range(2, phi):
            if gcd(i, phi) == 1:
                return i

    @staticmethod
    def get_reversed(key, phi):
        r, t = 0, 0
        new_t, new_r = 1, key

        while new_r != 0:
            q = r // new_r
            t, new_t = new_t, t - q * new_t
            r, new_r = new_r, r - q * new_r

        if t > 1:
            raise Exception

        if r < 0:
            t += phi

        return t

    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        # create key pairs(prime numbers)
        p, q = self.get_key(), self.get_key()
        self.mod = p * q
        phi = (p - 1) * (q - 1)

        encrypt_key = self.generate_key(phi)
        self.decrypt_key = self.get_reversed(encrypt_key, phi)

        # exchange public keys
        self.s.send(encrypt_key.to_bytes(128))
        self.s.send(self.mod.to_bytes(128))

        # receive the encrypted secret key
        self.server_key = self.s.recv(1024).decode()
        self.server_mod = self.s.recv(1024).decode()

        message_handler = threading.Thread(target=self.read_handler,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler,args=())
        input_handler.start()

    def read_handler(self): 
        while True:
            message = str(int.from_bytes(self.s.recv(1024)))
            key = int.from_bytes(self.s.recv(1024))
            mod = int.from_bytes(self.s.recv(1024))

            # decrypt message with the secrete key
            decrypted = str(pow(int(message), key, mod))

            if len(decrypted) % 3 != 0:
                decrypted = '0' + decrypted

            message = ''
            for i in range(0, len(decrypted), 3):
                message += chr(int(decrypted[i:i + 3]))

            print(message)

    def write_handler(self):
        while True:
            message = input()
            cipher = ''

            for char in message:
                cipher += f'{ord(char):03}'

            crypted_msg = pow(int(cipher), int(self.server_key), int(self.server_mod))
            self.s.send(str(crypted_msg).encode())

if __name__ == "__main__":
    cl = Client("127.0.0.1", 9010, "b_g")
    cl.init_connection()