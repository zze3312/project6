import json
import socket
import threading

user_nick_list = []
chat_list = []
nickname = ''
client_host = ''
msg_recv_yn = True

def connectClient(self, server_host = '127.0.0.1', server_port = 9997):
    print('connectClient 시작...')

    global nickname, client_host

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    client_host = client_socket.getsockname()[0]
    print(f'접속한 클라이언트 IP : {client_host}')

    # 정상적인 닉네임 입력할 때까지 반복
    while True:
        #nickname = input('닉네임 입력 : ')
        # 입력창에 입력한 닉네임 가져오기
        nickname = self.inputNick.text()

        send_data = {'status' : 'request', 'type' : 'nick', 'data' : nickname, 'user' : nickname, 'user_ip' : client_host, 'serial' : '' }
        client_socket.send(json.dumps(send_data).encode('utf-8'))
        print('닉네임 등록 요청....')

        # 서버에서 변환된 결과 가져와서 화면에 닉네임 셋팅
        data = client_socket.recv(8192)

        try:
            recv_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. connectClient : {data}")
            return

        if recv_data['type'] == 'nick' and recv_data['data'] == 'OK':
            print(f'닉네임 등록 요청 결과 받음.... : 정상')
            print(recv_data)
            self.userInfotxt_nick.setText(nickname)
            self.userInfotxt_ip.setText(client_host)

            break
        else:
            print(f'닉네임 등록 요청 결과 받음.... : 불량')
    print('connectClient 끝...')
    return client_socket

def sendMsg(sock, msg, room_serial):
    print('sendMsg 시작...')
    global nickname, client_host
    print(f'가져온 메세지 : {msg}')
    if msg != 'quit':
        print('나가기 요청이 아니어서 들어왔습니다...')
        send_data = {'status' : 'request', 'type' : 'msg', 'data' : msg, 'user' : nickname, 'user_ip' : client_host, 'serial' : room_serial }
        print(f'서버에게 보낼 데이터 : {send_data}')
        print(f'서버정보 : {sock}')
        sock.send(json.dumps(send_data).encode('utf-8'))
    else:
        print('나가기 요청이어서 들어왔습니다...')
        send_data = {'status': 'request', 'type': 'quit', 'data': '', 'user' : nickname, 'user_ip' : client_host, 'serial' : room_serial }
        print(f'서버에게 보낼 데이터 : {send_data}')
        sock.send(json.dumps(send_data).encode('utf-8'))

    print('sendMsg 끝...')

def recvMsg(self, sock):
    print('recvMsg 시작...')
    global nickname, client_host
    while True:
        print('메세지 채갈 준비중....')
        msg = sock.recv(8192)
        print('메세지 가져옴!!')

        try:
            recv_data = json.loads(msg.decode('utf-8'))
        except json.JSONDecodeError:
            print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. recvMsg : {msg}")
            return

        print(f'type : {recv_data['type']}')
        print(f'서버에게서 온 메세지 : {recv_data['data']}')
        if recv_data['data'] != 'OK_OLD' and recv_data['data'] != 'OK_NEW' and recv_data['data'] != 'OK':
            self.chatMsgList.addItem(recv_data['data'])

        if (recv_data['type'] == 'exit' and recv_data['user'] == nickname and recv_data['user_ip'] == client_host) or recv_data['type'] == 'rmroom':
            self.chatMsg.setDisabled(True)
            break
    print('recvMsg 끝...')

def getUserList(sock):
    print('getUserList 시작...')
    global user_nick_list, nickname, client_host
    send_data = {'status': 'request', 'type': 'user_list', 'data': '', 'user' : nickname, 'user_ip' : client_host, 'serial' : '' }
    sock.send(json.dumps(send_data).encode('utf-8'))

    msg = sock.recv(8192)

    try:
        recv_data = json.loads(msg.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. getUserList : {msg}")
        return

    print(f'접속자명단 : {recv_data['data']}')
    print('getUserList 끝...')
    return recv_data['data']

def getChatList(sock):
    print('getChatList 시작...')
    global user_nick_list, nickname, client_host
    send_data = {'status': 'request', 'type': 'chat_list', 'data': '', 'user' : nickname, 'user_ip' : client_host, 'serial' : '' }
    sock.send(json.dumps(send_data).encode('utf-8'))
    print('채팅창 목록 요청....')

    msg = sock.recv(8192)

    try:
        recv_data = json.loads(msg.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. getChatList : {msg}")
        return
    print(f'채팅창 목록 요청 응답 받음.... : ')
    print(f'채팅방 목록 : {recv_data['data']}')
    print('getChatList 끝...')

    return recv_data['data']

# 채팅방 생성 함수
def reqCreateChatRoom(self, sock):
    print('reqCreateChatRoom 시작...')
    global nickname, client_host
    # 입력한 채팅방 이름으로 생성되도록 수정 (팝업에서 가져옴)
    room_name = self.newChatTitle.text()
    max_cnt = self.newChatMemCnt.value()
    room_info = {'room_name' : room_name, 'max_cnt' : max_cnt}

    send_data = {'status': 'request', 'type': 'create_chat', 'data': room_info, 'user' : nickname, 'user_ip' : client_host, 'serial' : '' }
    sock.send(json.dumps(send_data).encode('utf-8'))
    print(f'접속자 {nickname} : 채팅방 생성 요청...')

    # 채팅방 생성 결과 응답 받기
    data = sock.recv(8192)
    try:
        recv_data = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. reqCreateChatRoom : {data}")
        return

    print(recv_data['data'])
    print('reqCreateChatRoom 끝...')

def reqConnectChat(self, sock, room_serial):
    print('reqConnectChat 시작...')
    send_data = {'status': 'request', 'type': 'connect_chat', 'data': '' , 'user': nickname, 'user_ip': client_host, 'serial' : room_serial}
    sock.send(json.dumps(send_data).encode('utf-8'))
    print(f'{room_serial} 에 입장 요청함...')

    data = sock.recv(8192)
    try:
        recv_data = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. reqConnectChat : {data}")
        return

    print(recv_data['data'])

    if recv_data['data'] != 'ER_MAXROOM':
        receiveThread = threading.Thread(target=recvMsg, args=(self, sock))
        receiveThread.start()

        send_data = {'status': 'request', 'type': 'enter_chat_msg', 'data': '', 'user': nickname, 'user_ip': client_host, 'serial': room_serial}
        sock.send(json.dumps(send_data).encode('utf-8'))
        print('reqConnectChat 끝...')

        return room_serial
    else:
        return ''