import socket
import re

def fncSetNick(self, nickname):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    client_socket.send(nickname.encode())

    receive_data = client_socket.recv(1024)
    nickname = f"{nickname}({receive_data.decode()})"

    print(f"닉네임이 {nickname}으로 설정되었습니다.")
    self.userInfotxt.setText(nickname)
    return client_socket

def sendMsg(self, client_socket):
    nickname = self.userInfotxt.text()
    msg = self.chatMsg.text()

    msg = (f"{nickname} : " + msg).encode()
    client_socket.send(msg)


def fncQuit():
    print("나가기 버튼 눌림")


def check_ip_format(ip_str):
    ip_format = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    if ip_format.match(ip_str) is not None:
        return True
    else:
        return False