import socket
import threading

ADMIN_DATA = {
    "Admin": "200210",
    "Admin2": "admin_password2"
}

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

clients = []
client_ips = []
nicknames = []
client_device_ids = []

def logo():
    print("""
    
 $$$$$$\  $$$$$$$$\ $$$$$$$\  $$\    $$\ $$$$$$$$\ $$$$$$$\        $$\    $$\  $$$$$$\  
$$  __$$\ $$  _____|$$  __$$\ $$ |   $$ |$$  _____|$$  __$$\       $$ |   $$ |$$  __$$\ 
$$ /  \__|$$ |      $$ |  $$ |$$ |   $$ |$$ |      $$ |  $$ |      $$ |   $$ |\__/  $$ |
\$$$$$$\  $$$$$\    $$$$$$$  |\$$\  $$  |$$$$$\    $$$$$$$  |      \$$\  $$  | $$$$$$  |
 \____$$\ $$  __|   $$  __$$<  \$$\$$  / $$  __|   $$  __$$<        \$$\$$  / $$  ____/ 
$$\   $$ |$$ |      $$ |  $$ |  \$$$  /  $$ |      $$ |  $$ |        \$$$  /  $$ |      
\$$$$$$  |$$$$$$$$\ $$ |  $$ |   \$  /   $$$$$$$$\ $$ |  $$ |         \$  /   $$$$$$$$\ 
 \______/ \________|\__|  \__|    \_/    \________|\__|  \__|          \_/    \________|
                                                                                        
                                                                                        
#########################################################################################
                                Created by: KelivnJudha
                                    Version: 1.0
                                 info: Server file                                                                                        
#########################################################################################
""")

def broadcast(message, to_admins_only=False):
    for client in clients:
        if to_admins_only and not nicknames[clients.index(client)].startswith("Admin-"):
            continue
        client.send(message)

def handle_connection(client, addr):
    client_ip = addr[0]
    client_ips.append(client_ip)

    stop = False
    while not stop:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(f"Message received: {message}")
            nickname = nicknames[clients.index(client)]
            if nickname.startswith("Admin-"):
                _, _, message_content = message.partition(": ")
                target_nickname, _, message_content = message.partition(": ")

                if message.startswith("-usr_info"):
                    client.send(active_users_info().encode("utf-8"))

                else:
                    print(f"Forwarding message to target: {target_nickname}")
                    send_message_to_target(target_nickname, message_content)
                    print(f"Message forwarded to target: {target_nickname}")
            else:
                admin_nickname, _, result_message = message.partition(": ")
                admin_nickname = admin_nickname.strip()
                if admin_nickname.startswith("Admin-"):
                    admin_nickname = f"Admin-{client_ip}"
                    send_message_to_target(admin_nickname,f"{nickname}: {result_message}")
                else:
                    broadcast(message.encode("utf-8"))

        except Exception as e:
            print(f"Error in handle connection: {e}")
            index = clients.index(client)
            clients.remove(client)
            client_ips.remove(client_ip)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            if not nickname.startswith("Admin-"):
                broadcast(f"{nickname} Disconnected".encode("utf-8"))
            stop = True

def active_users_info():
    user_count = len(nicknames)
    user_list = ", ".join(nicknames)
    return f"Number of active users: {user_count}\nNicknames: {user_list}"

def send_message_to_target(target_nickname, message):
    target_found = False
    for index, nickname in enumerate(nicknames):
        if nickname == target_nickname:
            target_found = True
            target_client = clients[index]
            target_client.send(f"Admin: {message}".encode("utf-8"))
            print(f"Message sent to target: {target_nickname}")
            break
    if not target_found:
        admin_index = [i for i, nickname in enumerate(nicknames) if nickname.startswith("Admin-") ]
        if admin_index:
            admin_client = clients[admin_index[0]]
            admin_client.send(f"User '{target_nickname}' not found".encode("utf-8"))
        else:
            print(f"User with IP '{target_nickname}' not found.")

def main():
    server.listen()
    print("Server is running...")
    while True:
        client, addr = server.accept()
        ip, _ = addr

        client.send("ENTER NICKNAME:".encode('utf-8'))
        username = client.recv(1024).decode("utf-8")

        if username in ADMIN_DATA:
            client.send("ENTER PASSWORD:".encode('utf-8'))
            received_password = client.recv(1024).decode("utf-8")

            if received_password == ADMIN_DATA[username]:
                client.send("PASSWORD accepted. You are now connected!".encode('utf-8'))
                client.send(active_users_info().encode('utf-8'))
                nickname = f"Admin-{ip}"
                nicknames.append(nickname)
                clients.append(client)
                print(f"Nickname is {nickname}")
                broadcast(f"{nickname} Connected".encode('utf-8'))
                thread = threading.Thread(target=handle_connection, args=(client, addr))
                thread.start()
            else:
                client.send("Invalid PASSWORD. Connection refused.".encode('utf-8'))
                client.close()
                continue
        else:
            client.send("ENTER DEVICE ID:".encode("utf-8"))
            device_id = client.recv(1024).decode("utf-8")
            print(f"Connected to {addr}")
            nickname = f"{username}-{device_id}"
            nicknames.append(nickname)
            client_ips.append(ip)
            client_device_ids.append(device_id)
            clients.append(client)
            print(f"Nickname is {nickname}")
            broadcast(f"{nickname} Connected".encode('utf-8'), to_admins_only=True)
            client.send("You are now connected!".encode('utf-8'))
            thread = threading.Thread(target=handle_connection, args=(client, addr))
            thread.start()

if __name__ == "__main__":
    logo()
    main()