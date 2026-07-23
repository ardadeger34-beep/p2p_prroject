import socket
import json
import os
import base64
import threading
import random
import pyDes
from datetime import datetime


def handle_client(client_socket, client_address):
    print("Connection established.")
    print(client_address)

    data = client_socket.recv(1024)
    message = data.decode()
    json_message = json.loads(message)

    if "key" in json_message:
        print("Key exchange request has arrived.")

        p = 907
        g = 7

        remote_public_key = int(json_message["key"])

        private_key = random.randint(2, p - 2)
        public_key = pow(g, private_key, p)

        response = {
            "key": str(public_key)
        }

        client_socket.send(json.dumps(response).encode())

        shared_secret = pow(remote_public_key, private_key, p)

        print("Uploader shared secret:")
        print(shared_secret)

        des_key_string = str(shared_secret).zfill(8)[:8]
        des_key_bytes = des_key_string.encode("utf-8")

        print("DES key:")
        print(des_key_bytes)

        data = client_socket.recv(1024)
        message = data.decode()
        print("Second message raw:", repr(message))
        try:
            json_message = json.loads(message)
            print("Parsed successfully:", json_message)
        except Exception as e:
            print("JSON parse error:" , e)
            client_socket.close()
            return
        
        print("About to check json_message:", json_message)

    if "requested secured content" in json_message:
        requested_content = json_message["requested secured content"]
        file_path = os.path.join("chunks", requested_content)
        print("Looking for file:", file_path)
        print("Files in chunks folder:", os.listdir("chunks"))

        if not os.path.exists(file_path):
            response = {"error": "Content not found"}
            client_socket.send(json.dumps(response).encode())
            client_socket.close()
            return

        with open(file_path, "rb") as file:
            file_data = file.read()

            encrypted_bytes = pyDes.des(
            des_key_bytes,
            pyDes.ECB,
            pad=None,
            padmode=pyDes.PAD_PKCS5
        ).encrypt(file_data)

        encoded_encrypted_chunk = base64.b64encode(encrypted_bytes).decode("utf-8")

        response = {
            "chunk name": requested_content,
            "encrypted chunk": encoded_encrypted_chunk
        }

        client_socket.send(json.dumps(response).encode())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | {requested_content} | {client_address[0]} | SENT\n"

        with open("logs/sent_log.txt", "a") as log_file:
            log_file.write(log_line)
        print("Secure content isteği geldi:")
        print(requested_content)

        client_socket.close()
        return

    if "requested content" in json_message:
        requested_content = json_message["requested content"]
        file_path = os.path.join("chunks", requested_content)

        if not os.path.exists(file_path):
            response = {"error": "Content not found"}
            client_socket.send(json.dumps(response).encode())
            client_socket.close()
            return

        with open(file_path, "rb") as file:
            file_data = file.read()

        encoded_data = base64.b64encode(file_data).decode()

        response = {
            "chunk name": requested_content,
            "data": encoded_data
        }

        client_socket.send(json.dumps(response).encode())

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | {requested_content} | {client_address[0]} | SENT\n"

        with open("logs/sent_log.txt", "a") as log_file:
            log_file.write(log_line)

        print("Chunk has been sent to the client.")

    client_socket.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 6001))
server.listen()

print("Server is working.")

while True:
    client_socket, client_address = server.accept()

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    )

    client_thread.start()