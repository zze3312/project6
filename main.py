import sys
#import client
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
        self.reloadUserList.clicked.connect(self.fncUserListPage)
        #self.quitBtn.clicked.connect(client.fncQuit)
        #self.sendBtn.clicked.connect(client.sendMsg)

    def fncLogin(self):
        # 서버에 접속
        global client_socket
        client_socket = client.connectClient(self)
        print(client_socket)
        # 접속 후 메인화면으로 이동
        self.mainWidget.setCurrentIndex(1)
        self.fncUserListPage()

    def fncAdminPage(self):
        # 관리자 페이지
        self.mainWidget.setCurrentIndex(2)

    def fncMainPage(self):
        # 로그인 페이지
        self.mainWidget.setCurrentIndex(0)

    def fncUserListPage(self):
        global client_socket
        self.loginUserList.setColumnWidth(0, 390)
        client.getUserList(client_socket)


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

