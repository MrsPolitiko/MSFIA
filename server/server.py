import socket
import threading

clients = []
server_running = True

def handle_client(client_socket, addr):
    print(f"[+] Подключён {addr}")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{addr}] {message}")
            # Рассылаем сообщение всем клиентам
            for client in clients:
                if client != client_socket:
                    client.send(f"[{addr}] {message}".encode('utf-8'))
        except:
            if client_socket in clients:
                clients.remove(client_socket)
            client_socket.close()
            print(f"[-] Отключён {addr}")
            break

def server_input():
    global server_running
    while server_running:
        message = input()
        if message.lower() == 'exit':
            server_running = False
            broadcast("[Сервер] Сервер отключается...")
            break
        broadcast(f"[Сервер] {message}")

def broadcast(message):
    print(message)
    for client in clients.copy():  # Используем копию списка на случай изменений
        try:
            client.send(message.encode('utf-8'))
        except:
            if client in clients:
                clients.remove(client)
            client.close()

def start_server(host='127.0.0.1', port=5555):
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    server.settimeout(1)  # Устанавливаем таймаут для accept
    print(f"[*] Сервер запущен на {host}:{port}")
    print("Введите сообщение для отправки всем клиентам или 'exit' для выхода")

    # Запускаем поток для обработки ввода сервера
    input_thread = threading.Thread(target=server_input)
    input_thread.start()

    while server_running:
        try:
            client_socket, addr = server.accept()
            clients.append(client_socket)
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
            broadcast(f"[Сервер] Новый участник подключился: {addr}")
        except socket.timeout:
            continue
        except:
            break

    # Завершаем работу сервера
    for client in clients:
        client.close()
    server.close()
    print("[*] Сервер остановлен")

if __name__ == "__main__":
    start_server()
