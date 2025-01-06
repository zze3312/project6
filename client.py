import socket

def fncClient():
    print("닉네임을 입력해 주세요 : ")
    nickname = input()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    client_socket.send(nickname.encode())

    receive_data = client_socket.recv(1024)

    while receive_data.decode() != "OK":
        print("닉네임을 다시 입력해 주세요 : ")
        nickname = input()
        client_socket.send(nickname.encode())
        receive_data = client_socket.recv(1024)

    print(f"닉네임이 {nickname}으로 설정되었습니다.")

    while receive_data.decode() != "BYE":
        print(f"입력 : ")
        msg = input()

        msg = (f"{nickname} : " + msg).encode()
        client_socket.send(msg)

        print("Received:", receive_data.decode())


def fncQuit():
    print("나가기 버튼 눌림")