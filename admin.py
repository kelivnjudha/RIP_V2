import socket
import threading

IP = "191.101.229.172"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            print(message)
        except:
            print("An error occurred.")
            client.close()
            break

def send_messages():
    target_ip = input("Enter the IP address of the user you want to message: ")
    while True:
        message_content = input(f"{target_ip}~> ")
        if message_content.startswith("-ch_ip"):
            new_ip = message_content.split(" ")[1]
            target_ip = new_ip
            print(f"Target IP changed to {new_ip}")
            continue
        message = f"{target_ip}: {message_content}"
        client.send(message.encode("utf-8"))


def connect_to_server():
    client.connect((IP, PORT))
    message = client.recv(1024).decode('utf-8')
    if message == "ENTER ID:":
        client.send(input(">").encode('utf-8'))
    
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages)
    send_thread.start()

if __name__ == "__main__":
    connect_to_server()
