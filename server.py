import socket
import threading

client_cnt = int()
client_socket_list = list()

def startServer():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address_ip = '127.0.0.1'
    server_address_port = 9999
    server_address = (server_address_ip, server_address_port)
    print(server_address)

    server_sock.bind(server_address)
    server_sock.listen(5)

    print("서버가 실행되었습니다.")
    try:
        while True:
            client_socket, client_addr = server_sock.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
            thread.start()

    except Exception as e:
        print("에러 : ", e)

    finally:
        server_sock.close()

def handle_client(client_socket, client_address):
    nick_validate = False
    global client_socket_list
    print(f"{client_address}에서 접속이 확인되었습니다.")

    while not nick_validate:
        data = client_socket.recv(1024).decode()
        print("클라이언트 : ", data)

        if not data:
            client_socket.send("NOT".encode())
        else:
            nick_validate = True
            client_socket_list.append(client_socket)
            client_socket.send(client_address[0].encode())

    data = client_socket.recv(1024).decode()
    send_msg(client_socket_list, data)


# 접속자에게 메세지 전달
def send_msg(client_socket_list, msg):
    lock = threading.Lock()
    lock.acquire()
    for client_socket in client_socket_list:
        client_socket.send(msg)
    lock.release()