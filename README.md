# Discrete Laboratory work №2
> by Władysław Danylyshyn and Iia Maharyta 


## Files

The whole `client.py` file is Władysław's Danylyshyn work.

### Functions 
#### miller_rabin(n: int)
Function that checks if the number is prime or not using Miller-Rabin rule. It is used
when generating keys and mods for client or server

#### get_key()
Function that just generates a huge prime numbers. Range: [`10^100`, `10^101`]

#### generate_key(phi: int)
Function that generates public key. It checks if the number is coprime
with the phi number

#### get_reversed(key: int, phi: int)
Function that generates private key(reversed to public according to the phi)

#### init_connection()
Generates the main socket for communication with server and exchanges with keys

#### read_handler()
Gets the recent message and key to decode the message

#### write_handler()
Encodes the message and sends it to the server