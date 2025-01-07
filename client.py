import json
import socket
import threading

user_nick_list = []
chat_list = []

def connectClient(self, server_host = '127.0.0.1', server_port = 9997):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    # 정상적인 닉네임 입력할 때까지 반복
    while True:
        global nickname
        #nickname = input('닉네임 입력 : ')
        # 입력창에 입력한 닉네임 가져오기
        nickname = self.inputNick.text()

        send_data = {'status' : 'request', 'type' : 'nick', 'data' : nickname }
        client_socket.send(json.dumps(send_data).encode('utf-8'))
        print('닉네임 등록 요청....')

        # 서버에서 변환된 결과 가져와서 화면에 닉네임 셋팅
        data = client_socket.recv(1024)

        try:
            recv_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print("잘못된 JSON 형식의 데이터가 들어왔습니다.")
            return

        if recv_data['type'] == 'nick' and recv_data['data'] == 'OK':
            print(f'닉네임 등록 요청 결과 받음.... : 정상')
            print(recv_data)
            send_data = {'status': 'request', 'type': 'nick', 'data': 'THANKS'}
            client_socket.send(json.dumps(send_data).encode('utf-8'))
            break
        else:
            send_data = {'status': 'request', 'type': 'nick', 'data': recv_data['data']}
            client_socket.send(json.dumps(send_data).encode('utf-8'))
            print(f'닉네임 등록 요청 결과 받음.... : 불량')

    return client_socket


    # print(f'스레드 생성 전 소켓 : {client_socket}')
    # sendThread = threading.Thread(target=sendMsg, args=(client_socket,))
    # receiveThread = threading.Thread(target=recvMsg, args=(client_socket,))
    # sendThread.start()
    # receiveThread.start()
    #
    # # sendThread와 receiveThread가 종료될 때까지 대기
    # sendThread.join()
    # receiveThread.join()
    #
    # client_socket.close()



def sendMsg(sock):
    global nickname
    # nickname = self.userInfotxt.text()
    # msg = self.chatMsg.text()
    print(sock)
    while True:
        msg = input()
        if msg != 'quit':
            print('나가기 요청이 아니어서 들어왔습니다...')
            send_data = {'status' : 'request', 'type' : 'msg', 'data' : msg, 'user' : nickname }
            print(f'서버에게 보낼 데이터 : {send_data}')
            print(f'서버정보 : {sock}')
            
            sock.send(json.dumps(send_data).encode('utf-8'))
        else:
            print('나가기 요청이어서 들어왔습니다...')
            send_data = {'status': 'request', 'type': 'quit', 'data': '', 'user' : nickname }
            print(f'서버에게 보낼 데이터 : {send_data}')
            sock.send(json.dumps(send_data).encode('utf-8'))
            break

def recvMsg(sock):
    while True:
        msg = sock.recv(1024)
        try:
            recv_data = json.loads(msg.decode('utf-8'))
        except json.JSONDecodeError:
            print("잘못된 JSON 형식의 데이터가 들어왔습니다.")
            return

        # TODO : 화면에 뿌려주는 기능으로 변경
        print(recv_data['data'])

def fncQuit():
    print('나가기 버튼 눌림')


def getUserList(sock):
    global user_nick_list
    send_data = {'status': 'request', 'type': 'user', 'data': '', 'user' : nickname }
    sock.send(json.dumps(send_data).encode('utf-8'))

    msg = sock.recv(1024)

    try:
        recv_data = json.loads(msg.decode('utf-8'))
    except json.JSONDecodeError:
        print("잘못된 JSON 형식의 데이터가 들어왔습니다.")
        return

    print(f'접속자명단 : {recv_data['data']}')

# connectClient()