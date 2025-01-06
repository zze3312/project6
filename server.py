import socket
import threading

client_list = []


def handle_client(client_socket, client_address):
    nickValidate = False
    print(f'{client_address}에서 접속이 확인되었습니다.')
    while not nickValidate:
        data = client_socket.recv(1024).decode()
        # 닉네임 유효성 검사
        if not data:
            client_socket.send("NOT".encode())
        else:
            nickValidate = True
            client_socket.send("OK".encode())


    # 접속한 사람들 대화
    while True:
        data = client_socket.recv(1024).decode()

        if not data:
            break
        if data == "q":
            client_socket.send("BYE".encode())
            client_socket.close()

        client_socket.send(data.encode())


def startServer():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8080)
    server_socket.bind(server_address)
    server_socket.listen(5)

    print('서버가 시작되었습니다')

    while True:
        client_socket, client_address = server_socket.accept()
        client_list.append(client_address)

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

    server_socket.close()