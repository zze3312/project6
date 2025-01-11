import json
import socket
import threading
import random
import string
import re
import pymysql
from queue import Queue

client_socket_list = []
user_nick_list = []
chat_list = []
chat_member_list = []


def startServer(host='127.0.0.1', port = 9999):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 서버 닫힐 때 클라이언트 전부 connect 끊기
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    print(f'서버가 실행되었습니다 : {host} {port}')

    global sock_cnt, client_socket_list

    while True:
        client_socket, client_addr = server_sock.accept()
        client_socket_list.append(client_socket)

        # 소켓에 연결된 각각의 클라이언트의 메시지에 응답할 쓰레드
        thread = threading.Thread(target=clntHandler, args=(client_socket, ))
        thread.start()

        # TODO : 실시간 목록을 불러오게 할 쓰레드 추가??


# 메세지 전달
def sendMsg(socket_list, data):
    # [{'user': req['user'], 'user_ip' : req['user_ip'], 'conn': conn}]
    # [message, conn, count]
    print(f'메세지 돌릴 목록 : {socket_list}')
    try:
        # for 문을 돌면서 모든 클라이언트에게 동일한 메시지를 보냄
        for sock in socket_list:
            print(f'이사람에게 보냄 : {sock}')
            print(f'sendMsg -> data : {data}')
            # client 본인이 보낸 메시지도 메세지내역에 보여야하므로 제한하지 않음
            print(f'클라이언트에게 전송한 메세지 : {data}')
            print(f'소켓정보 : {sock['conn']}')
            data['data'] = chatFiltering(data['data'])
            sock['conn'].send(json.dumps(data).encode('utf-8'))
    except:
        pass


def clntHandler(conn):
    global user_nick_list, chat_list
    while True:
        print('메세지 전달 요청 기다리는중...')
        data = conn.recv(8192)
        print('메세지 전달 요청 받음...')
        try:
            message = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print(f'잘못된 JSON 형식의 데이터가 들어왔습니다. clntHandler : {data}')
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
            exitChatRoom(message)
        # msg : 메세지 전송
        elif message['type'] == 'msg':
            sendMessage(message)
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
            enterChatRoom(message)
        elif message['type'] == 'word_list':
            word_list = getBadWordList()
            print(f'클라이언트에게 보낼 단어목록 : {word_list}')
            message['data'] = word_list
            conn.send(json.dumps(message).encode('utf-8'))
        elif message['type'] == 'add_word':
            result = addWord(message['data'])
            message['data'] = result
            conn.send(json.dumps(message).encode('utf-8'))
        elif message['type'] == 'remove_word':
            result = removeWord(message['data'])
            message['data'] = result
            conn.send(json.dumps(message).encode('utf-8'))
        elif message['type'] == 'room_info':
            room_info = searchRoomInfo(message['data'])
            print(f'room_info : {room_info}')
            message['data'] = room_info
            conn.send(json.dumps(message).encode('utf-8'))
        else:
            pass
        # 각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄

def sendMessage(req):
    print(f'접속한 방에 채팅내용을 보냅니다!! 방 serial : {req['serial']}')
    global chat_member_list
    for chat_member in chat_member_list:
        if chat_member['serial'] == req['serial']:
            print(f'serial이 맞는 방을 찾았어요! 이방의 멤버는 : {chat_member['user_list']}')
            req['data'] = '< ' + req['user'] + ' > ' + req['data']
            print(f'이렇게 메세지를 보낼게요... : {req['data']}')
            sendMsg(chat_member['user_list'], req)

# 채팅방 입장 메세지 전달
def enterChatRoom(req):
    global chat_member_list
    for chat_member in chat_member_list:
        print(f'for문 들어와서 챗 멤버를 확인해볼게요 : {chat_member}')
        if chat_member['serial'] == req['serial']:
            print(f'serial이 맞는 방을 찾았어요! 이방의 멤버는 : {chat_member['user_list']}')
            req['data'] = '< ' + req['user'] + ' > 님이 입장하셨습니다.'
            sendMsg(chat_member['user_list'], req)

# 채팅방 퇴장 메세지 전달
def exitChatRoom(req):
    global chat_member_list, chat_list
    for chat_member in chat_member_list:
        print(f'for문 들어와서 챗 멤버를 확인해볼게요 : {chat_member}')
        if chat_member['serial'] == req['serial']:
            print(f'serial이 맞는 방을 찾았어요! 이방의 멤버는 : {chat_member['user_list']}')


            # 채팅방 주인이 나가면 방 폭발 / 채팅방 주인 아니면 채팅방 현재인원 1감소
            chat_idx = 0
            for chat_info in chat_list:
                if chat_info['serial'] == req['serial']:
                    if chat_info['owner'] == req['user'] and chat_info['owner_ip'] == req['user_ip']:
                        # 방없어졌다는 메세지 보내기
                        req['type'] = 'rmroom'
                        req['data'] = '방장이 퇴장하여 채팅방이 사라졌습니다.'
                        sendMsg(chat_member['user_list'], req)
                        # 방없애기
                        del chat_list[chat_idx]
                    else:
                        chat_info['now_cnt'] -= 1
                        mem_index = 0
                        for member in chat_member['user_list']:
                            if member['user'] == req['user'] and member['user_ip'] == req['user_ip']:
                                del chat_member['user_list'][mem_index]
                                break
                            mem_index += 1
                        break
                chat_idx += 1

            req['type'] = 'exit'
            req['data'] = '< ' + req['user'] + ' > 님이 퇴장하셨습니다.'
            sendMsg(chat_member['user_list'], req)
            break

# 채팅방 접속
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
                    if chat_info['max_cnt'] < chat_info['now_cnt']:
                        chat_info['now_cnt'] -= 1
                        send_data = {'status': 'response', 'type': 'connect_chat', 'data': 'ER_MAXROOM', 'user': req['user'], 'user_ip': req['user_ip'], 'serial': req['serial']}
                        conn.send(json.dumps(send_data).encode('utf-8'))
                        return
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
    room_info = {'serial' : room_serial, 'room_name' : req['data']['room_name'], 'owner' : req['user'], 'owner_ip' : req['user_ip'], 'max_cnt' : req['data']['max_cnt'], 'now_cnt' : 0}
    chat_list.append(room_info)

    # 채팅방 접속자 목록에 넣을 데이터
    room_info2 = { 'serial' : room_info['serial'], 'user_list' : [] }
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

# 채팅 비속어 필터링
def chatFiltering(str):
    # 금지어 관리에서 등록해놓은 단어 걸림
    word_list = getBadWordList()
    for word in word_list:
        str = re.sub(word['word'], '***', str)
    return str

def dbConn():
    conn = pymysql.connect(host='127.0.0.1', user='jh', password='admin', db='project6', charset='utf8')
    return conn

def dbClose(conn):
    conn.close()

def getBadWordList():
    bad_word_list = []

    conn = dbConn()
    cur = conn.cursor()
    sql = 'select seq, word from bad_word'
    cur.execute(sql)

    while True:
        row = cur.fetchone()
        print(row)
        if row == None:
            break

        bad_word_list.append({'seq': row[0], 'word': row[1]})

    dbClose(conn)
    return bad_word_list

def addWord(word):
    conn = dbConn()
    cur = conn.cursor()
    sql = 'insert into bad_word values(default, \'' + word + '\')'
    print(sql)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        print("insert 오류!")
        return 'ER'
    finally:
        dbClose(conn)
        
    return 'OK'

def removeWord(seq):
    conn = dbConn()
    cur = conn.cursor()
    sql = 'delete from bad_word where seq = \'' + str(seq) + '\''
    print(sql)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        print("delete 오류!")
        return 'ER'
    finally:
        dbClose(conn)

    return 'OK'

def searchRoomInfo(serial):
    for room in chat_list:
        if room['serial'] == serial:
            return room