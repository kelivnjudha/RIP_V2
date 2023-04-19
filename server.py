import socket
import threading

ADMIN_DATA = {
    "enter admin ip": "make admin pwd",
    "enter admin ip": "make admin pwd"
}

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

clients = []
client_ips = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_connection(client, addr):
    client_ip = addr[0]
    client_ips.append(client_ip)

    stop = False
    while not stop:
        try:
            message = client.recv(1024).decode("utf-8")
            target_ip, _, message_content = message.partition(": ")

            if client in clients and nicknames[clients.index(client)].startswith("Admin-"):
                send_message_to_target(target_ip, message_content)
            else:
                broadcast(message.encode("utf-8"))

        except:
            index = clients.index(client)
            clients.remove(client)
            client_ips.remove(client_ip)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} Disconnected".encode("utf-8"))
            stop = True

def active_users_info():
    user_count = len(nicknames)
    user_list = ", ".join(nicknames)
    return f"Number of active users: {user_count}\nNicknames: {user_list}"

def send_message_to_target(target_ip, message):
    if target_ip in client_ips:
        index = client_ips.index(target_ip)
        target_client = clients[index]
        target_client.send(f"Admin: {message}".encode("utf-8"))
    else:
        print(f"User with IP '{target_ip}' not found.")

def main():
    server.listen()
    print("Server is running...")
    while True:
        client, addr = server.accept()
        ip, _ = addr

        if ip in ADMIN_DATA:
            client.send("ENTER ID:".encode('utf-8'))
            received_id = client.recv(1024).decode("utf-8")

            if received_id == ADMIN_DATA[ip]:
                client.send("ID accepted. You are now connected!".encode('utf-8'))
                client.send(active_users_info().encode('utf-8'))
                nickname = f"Admin-{ip}"
                nicknames.append(nickname)
                clients.append(client)
                print(f"Nickname is {nickname}")
                broadcast(f"{nickname} Connected".encode('utf-8'))
                thread = threading.Thread(target=handle_connection, args=(client, addr))
                thread.start()
            else:
                client.send("Invalid ID. Connection refused.".encode('utf-8'))
                client.close()
                continue
        else:
            print(f"Connected to {addr}")
            client.send("ID".encode('utf-8'))
            nickname = client.recv(1024).decode("utf-8")
            nicknames.append(nickname)
            clients.append(client)
            print(f"Nickname is {nickname}")
            broadcast(f"{nickname} Connected".encode('utf-8'))
            client.send("You are now connected!".encode('utf-8'))
            thread = threading.Thread(target=handle_connection, args=(client, addr))
            thread.start()

if __name__ == "__main__":
    main()