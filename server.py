import json
import socket
import threading
from queue import Queue

sock_cnt = 0
client_socket_list = []
user_nick_list = []
chat_list = []

def startServer(host='127.0.0.1', port = 9997):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    print(f'서버가 실행되었습니다 : {host} {port}')

    global sock_cnt, client_socket_list
    send_queue = Queue()

    while True:
        sock_cnt += 1
        client_socket, client_addr = server_sock.accept()
        client_socket_list.append(client_socket)

        data = client_socket.recv(1024)
        print('닉네임 등록 요청 받음....')
        try:
            recv_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print("잘못된 JSON 형식의 데이터가 들어왔습니다.")
            return

        while True:
            if recv_data['data'] != '':
                user_nick_list.append(recv_data['data'])
                send_data = {'status': 'response', 'type': 'nick', 'data': 'OK'}
            else:
                send_data = {'status': 'response', 'type': 'nick', 'data': 'ER'}
                print('닉네임 이상해....')

            client_socket.send(json.dumps(send_data).encode('utf-8'))
            print('닉네임 등록 요청 처리 결과 보냄...')
            print(f'클라이언트 결과 확인 중...{sock_cnt}')
            data = client_socket.recv(1024)
            try:
                recv_data = json.loads(data.decode('utf-8'))
                print(recv_data)
            except json.JSONDecodeError:
                print(f"잘못된 JSON 형식의 데이터가 들어왔습니다. :  {repr(data)}")
                return
            if recv_data['type'] == 'nick' and recv_data['data'] == 'THANKS':
                break

        if sock_cnt > 1:
            send_queue.put('NEW CONN')
            sTread = threading.Thread(target=send_msg, args=(client_socket_list, send_queue))
            sTread.start()
            pass
        else:
            sTread = threading.Thread(target=send_msg, args=(client_socket_list, send_queue))
            sTread.start()

        # 소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
        rThread = threading.Thread(target=recv_msg, args=(client_socket, sock_cnt, send_queue))
        rThread.start()


# 접속자에게 메세지 전달
def send_msg(client_socket_list, send_queue):
    while True:
        try:
            # 새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
            if recv == 'NEW CONN':
                print('NEW CONN')
                break

            # for 문을 돌면서 모든 클라이언트에게 동일한 메시지를 보냄
            for client_socket in client_socket_list:
                data = recv[0]

                if recv[1] != client_socket:
                    # client 본인이 보낸 메시지는 받을 필요가 없기 때문에 제외시킴
                    print(data)
                    client_socket.send(json.dumps(data).encode('utf-8'))
                else:
                    if data['type'] == 'exit':
                        client_socket.send(json.dumps(data).encode('utf-8'))
                        client_socket.close()
        except:
            pass


def recv_msg(conn, count, send_queue):
    global user_nick_list
    while True:
        data = conn.recv(1024)
        print('메세지 전달 요청 받음...')
        try:
            message = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            print("잘못된 JSON 형식의 데이터가 들어왔습니다.")
            return

        print(f'클라이언트로부터 받은 메세지 : {message}')

        if message['type'] == 'quit':
            message['type'] = 'exit'
            message['data'] = '< ' + message['user'] + ' > 님이 퇴장하셨습니다'
            user_nick_list.remove(message['user'])
            send_queue.put([message, conn, count])
        elif message['type'] == 'msg':
            message['data'] = '< ' + message['user'] + ' > ' + message['data']
            send_queue.put([message, conn, count])
        elif message['type'] == 'user':
            print("여긴 왔어요~ ")
            message['data'] = user_nick_list
            conn.send(json.dumps(message).encode('utf-8'))
        else:
            pass
        # 각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄

