import socket
import threading
import re

nickname = ""

def fncSetNick(client_socket):
    global nickname
    print("닉네임 입력 : ")
    nickname = input()
    client_socket.send(nickname.encode())
    receive_data = client_socket.recv(1024)
    nickname = f"{nickname}({receive_data})"
    print(f"닉네임이 {nickname}으로 설정되었습니다.")
    return nickname

def sendMsg(client_socket):
    # nickname = self.userInfotxt.text()
    # msg = self.chatMsg.text()
    while True:
        msg = input()
        if msg != "quit":
            msg = f"{nickname} : {msg}"
            client_socket.send(msg.encode())
        else:
            client_socket.send(msg.encode())
            break

def recvMsg(client_socket):
    while True:
        msg = client_socket.recv(1024).decode()
        if msg == "BYE": break
        print(msg)

def fncQuit():
    print("나가기 버튼 눌림")

def connectClient():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 9999))
    client_socket.send(nickname.encode())

    nick = fncSetNick(client_socket)
    print(f"{nick} 접속 성공")

    sendThread = threading.Thread(target=sendMsg, args=(client_socket, ))
    receiveThread = threading.Thread(target=recvMsg, args=(client_socket, ))
    sendThread.start()
    receiveThread.start()
    client_socket.close()

connectClient()