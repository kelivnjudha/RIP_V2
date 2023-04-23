import socket
import threading

HOST = "191.101.229.172"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.startswith("ENTER NICKNAME:"):
                client.send(input("Username: ").encode("utf-8"))
            elif message.startswith("ENTER PASSWORD:"):
                client.send(input("Password: ").encode("utf-8"))
            elif message == "PASSWORD accepted. You are now connected!":
                print(message)
                active_users_message = client.recv(1024).decode("utf-8")
                print(active_users_message)
                main()
            else:
                print(message)
        except:
            print("An error occurred.")
            client.close()
            break

def send_message(target_nickname, message):
    client.send(f"{target_nickname}: {message}".encode("utf-8"))

def change_target():
    target_nickname = input("Enter the nickname of the user you want to message: ")
    return target_nickname

def main():
    target_nickname = change_target()
    while True:
        message = input(f"{target_nickname}~> ")
        if message == "-ch_tg":
            target_nickname = change_target()
        else:
            send_message(target_nickname, message)

if __name__ == "__main__":
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
