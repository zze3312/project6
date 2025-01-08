import sys
#import client
from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
from PyQt5 import uic

import client

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("main.ui")[0]
client_socket = ''

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("채팅창")
        self.mainWidget.setCurrentIndex(0)
        self.loginBtn.clicked.connect(self.fncLogin)
        self.adminBtn.clicked.connect(self.fncAdminPage)
        self.goMainBtn.clicked.connect(self.fncMainPage)
        self.createChatBtn.clicked.connect(self.createChat)
        self.connectChatBtn.clicked.connect(self.enterChat)
        self.reloadUserList.clicked.connect(self.fncUserListPage)
        self.reloadChatList.clicked.connect(self.fncChatListPage)
        self.chatList.cellDoubleClicked.connect(self.enterChat)
        #self.quitBtn.clicked.connect(client.fncQuit)
        self.sendBtn.clicked.connect(self.fncSendMsg)

    def fncLogin(self):
        # 서버에 접속
        global client_socket
        client_socket = client.connectClient(self)
        # 접속 후 메인화면으로 이동
        self.mainWidget.setCurrentIndex(1)

        self.fncUserListPage()
        self.fncChatListPage()

    def fncAdminPage(self):
        # 관리자 페이지
        self.mainWidget.setCurrentIndex(2)

    def fncMainPage(self):
        # 로그인 페이지
        self.mainWidget.setCurrentIndex(0)

    def fncUserListPage(self):
        global client_socket
        self.loginUserList.setColumnWidth(0, 440)
        login_list = client.getUserList(client_socket)
        print(login_list)

        rowCnt = len(login_list)
        self.loginUserList.setRowCount(rowCnt)

        for row in range(rowCnt):
            login_user = login_list[row]['user'] + '(' + login_list[row]['user_ip'] + ')'

            item = QTableWidgetItem(login_user)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.loginUserList.setItem(row, 0, item)

    def fncChatListPage(self):
        global client_socket
        self.chatList.setColumnWidth(0, 440)
        chat_list = client.getChatList(client_socket)

        rowCnt = len(chat_list)
        self.chatList.setRowCount(rowCnt)

        for row in range(rowCnt):
            login_user = chat_list[row]['room_name']

            item = QTableWidgetItem(login_user)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.chatList.setItem(row, 0, item)

    def createChat(self):
        global client_socket
        client.reqCreateChatRoom(self, client_socket)
        self.fncChatListPage()

    def enterChat(self, row, col):
        data = self.chatList.item(row, col)
        client.reqConnectChat(self, client_socket, data.text())

    def fncSendMsg(self):
        global client_socket
        msg = self.chatMsg.text()
        client.sendMsg(client_socket, msg)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

