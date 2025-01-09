import json
import socket
import threading
import random
import string
from queue import Queue

sock_cnt = 0
client_socket_list = []
user_nick_list = []
chat_list = []
chat_member_list = []

def startServer(host='127.0.0.1', port = 9997):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 서버 닫힐 때 클라이언트 전부 connect 끊기
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    print(f'서버가 실행되었습니다 : {host} {port}')

    global sock_cnt, client_socket_list
    send_queue = Queue()

    while True:
        sock_cnt += 1
        client_socket, client_addr = server_sock.accept()
        client_socket_list.append(client_socket)

        # 소켓에 연결된 각각의 클라이언트의 메시지에 응답할 쓰레드
        thread = threading.Thread(target=clnt_handler, args=(client_socket, sock_cnt, send_queue))
        thread.start()

        # TODO : 실시간 목록을 불러오게 할 쓰레드 추가??


# 메세지 전달
def send_msg(socket_list, data):
    # [{'user': req['user'], 'user_ip' : req['user_ip'], 'conn': conn}]
    # [message, conn, count]
    print(f'메세지 돌릴 목록 : {socket_list}')
    try:
        # for 문을 돌면서 모든 클라이언트에게 동일한 메시지를 보냄
        for sock in socket_list:
            print(f'이사람에게 보냄 : {sock}')
            print(f'send_msg -> data : {data}')
            sock['conn']
            if data['type'] == 'exit':
                sock['conn'].send(json.dumps(data).encode('utf-8'))
                sock['conn'].close()
            # client 본인이 보낸 메시지도 메세지내역에 보여야하므로 제한하지 않음
            print(f'클라이언트에게 전송한 메세지 : {data}')

            print(f'소켓정보 : {sock['conn']}')
            sock['conn'].send(json.dumps(data).encode('utf-8'))
    except:
        pass


def clnt_handler(conn, count, send_queue):
    global user_nick_list, chat_list
    while True:
        print('메세지 전달 요청 기다리는중...')
        data = conn.recv(8192)
        print('메세지 전달 요청 받음...')
        try:
            message = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. clnt_handler : {data}")
            return

        print(f'클라이언트로부터 받은 메세지 : {message}')
        # 상태값 response(서버에서 응답)으로 변경
        message['status'] = 'response'

        # type에 따른 분기처리
        # TODO : 기능 추가 예정
        # nick : 닉네임 등록
        if message['type'] == 'nick':
            print('닉네임 등록 요청 받음....')
            # 닉네임으로 설정할 값이 정상적으로 들어왔을 경우
            if message['data'] != '':
                # 접속자 목록에 넣을 데이터 생성
                user_info = {'user': message['data'], 'user_ip': message['user_ip']}
                # 접속자 목록에 추가
                user_nick_list.append(user_info)
                # 정상 처리 응답 생성
                send_data = {'status': 'response', 'type': 'nick', 'data': 'OK', 'user': message['data'], 'user_ip': message['user_ip'], 'serial' : message['serial']}
            else:
                # 처리 오류 응답 생성
                send_data = {'status': 'response', 'type': 'nick', 'data': 'ER', 'user': message['data'], 'user_ip': message['user_ip'], 'serial' : message['serial']}
                print('닉네임 이상해....')

            # 결과 전송
            conn.send(json.dumps(send_data).encode('utf-8'))
            print('닉네임 등록 요청 처리 결과 보냄...')

        # quit : 접속종료
        elif message['type'] == 'quit':
            message['type'] = 'exit'
            message['data'] = '< ' + message['user'] + ' > 님이 퇴장하셨습니다'
            send_message(message)
            # TODO : 퇴장 프로세스 추가
            #user_nick_list.remove(message['user'])
            #send_queue.put([message, conn, count])
        # msg : 메세지 전송
        elif message['type'] == 'msg':
            send_message(message)
        # user_list : 접속자 목록 불러오기
        elif message['type'] == 'user_list':
            message['data'] = user_nick_list
            # 요청자만 reload 해야하므로 직접 send함
            conn.send(json.dumps(message).encode('utf-8'))
        # chat_list : 채팅방 목록 불러오기
        elif message['type'] == 'chat_list':
            message['data'] = chat_list
            print(f'데이터 크기 : {len(chat_list)} / 채팅방 리스트 : {chat_list}')
            # 요청자만 reload 해야하므로 직접 send함
            conn.send(json.dumps(message).encode('utf-8'))
        # create_chat : 채팅방 생성
        elif message['type'] == 'create_chat':
            createChatRoom(conn, message)
        # connect_chat : 채팅방 접속
        elif message['type'] == 'connect_chat':
            connectChatRoom(conn, message)
        elif message['type'] == 'enter_chat_msg':
            print('여기 왔어용....')
            enterChatRoom(message)
        else:
            pass
        # 각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄

def send_message(req):
    print(f'접속한 방에 채팅내용을 보냅니다!! 방 serial : {req['serial']}')
    global chat_member_list
    for chat_member in chat_member_list:
        if chat_member['serial'] == req['serial']:
            print(f'serial이 맞는 방을 찾았어요! 이방의 멤버는 : {chat_member['user_list']}')
            req['data'] = '< ' + req['user'] + ' > ' + req['data']
            print(f'이렇게 메세지를 보낼게요... : {req['data']}')
            send_msg(chat_member['user_list'], req)

# 채팅방 입장 메세지 전달
def enterChatRoom(req):
    global chat_member_list
    for chat_member in chat_member_list:
        print(f'for문 들어와서 챗 멤버를 확인해볼게요 : {chat_member}')
        if chat_member['serial'] == req['serial']:
            print(f'serial이 맞는 방을 찾았어요! 이방의 멤버는 : {chat_member['user_list']}')
            req['data'] = '<' + req['user'] + ' >님이 입장하셨습니다.'
            send_msg(chat_member['user_list'], req)

# 채팅방 접속(목록에서)
def connectChatRoom(conn, req):
    global chat_list, chat_member_list
    serial = req['serial']
    # 해당 시리얼로 접속자 명단 찾기
    chat_num = 0
    print(f'해당 시리얼번호({serial})로 해당 방 멤버 확인중...')
    for chat_member in chat_member_list:
        if chat_member['serial'] == serial:
            print(f'시리얼번호({serial}) 일치하는 방을 찾았습니다!')
            # 해당 채팅방 참여자 정보에 일치하는 정보가 있으면 room_mem_yn을 True로 바꿈
            for chat_user in chat_member['user_list']:
                if chat_user['user'] == req['user'] and chat_user['user_ip'] == req['user_ip']:
                    print(f'< {req['user']} > 님은 이미 해당 방 멤버입니다.')
                    send_data = {'status': 'response', 'type': 'connect_chat', 'data': 'OK_OLD', 'user': req['user'], 'user_ip': req['user_ip'], 'serial' : req['serial']}
                    conn.send(json.dumps(send_data).encode('utf-8'))
                    return

            # 채팅방 멤버가 아니면 멤버등록
            print(f'< {req['user']} > 님을 해당 방의 멤버로 등록합니다...')
            # 멤버로 등록
            user_info = {'user': req['user'], 'user_ip' : req['user_ip'], 'conn': conn}
            chat_member['user_list'].append(user_info)

            # 채팅방 현재인원 1증가
            for chat_info in chat_list:
                if serial == chat_info['serial']:
                    chat_info['now_cnt'] += 1
                    break

            send_data = {'status': 'response', 'type': 'connect_chat', 'data': 'OK_NEW', 'user': req['user'], 'user_ip': req['user_ip'], 'serial' : req['serial']}
            conn.send(json.dumps(send_data).encode('utf-8'))
            return
        chat_num += 1

# 채팅방 생성(단체방)
def createChatRoom(conn, req):
    global chat_list
    # 채팅방 시리얼넘버 생성 -> 초대코드
    room_serial = createTocken(6)

    # 채팅방 목록에 넣을 데이터
    room_info = {'serial' : room_serial, 'room_name' : req['data'], 'owner' : req['user'], 'owner_ip' : req['user_ip'], 'max_cnt' : 10, 'now_cnt' : 1}
    chat_list.append(room_info)

    # 채팅방 접속자 목록에 넣을 데이터
    room_info2 = { 'serial' : room_info['serial'], 'user_list' : [{'user' : req['user'], 'user_ip' : req['user_ip'], 'conn' : conn}] }
    chat_member_list.append(room_info2)
    print(f'채팅 사용자 목록 : {chat_member_list}')

    # 정상 생성 되면 응답 보냄
    send_data = {'status': 'response', 'type': 'create_chat', 'data': 'OK', 'user': req['user'], 'user_ip': req['user_ip']}
    conn.send(json.dumps(send_data).encode('utf-8'))


# 채팅방 토큰 생성 (랜덤한 n자리 영문 대문자 문자열 생성)
def createTocken(n):
    global chat_list
    while True:
        rand_str = ''
        for i in range(n):
            rand_str += str(random.choice(string.ascii_uppercase))

        if rand_str not in chat_list:
            return rand_str