import sys
import client
from server import client_list
from PyQt5.QtWidgets import *
from PyQt5 import uic

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("main.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("제목")
        self.mainWidget.setCurrentIndex(0)
        self.loginBtn.clicked.connect(self.fncLogin)
        self.adminBtn.clicked.connect(self.fncAdminPage)
        self.goMainBtn.clicked.connect(self.fncMainPage)
        self.quitBtn.clicked.connect(client.fncQuit)
        self.sendBtn.clicked.connect(client.sendMsg)

    def fncLogin(self):
        # 입력창에 입력한 닉네임 가져오기
        nickname = self.inputNick.text()

        # 닉네임 셋팅 함수
        client_socket = client.fncSetNick(self, nickname)

        # 닉네임 셋팅 후 메인화면으로 이동
        self.mainWidget.setCurrentIndex(1)
        self.fncUserListPage()


    def fncAdminPage(self):
        # 관리자 페이지
        self.mainWidget.setCurrentIndex(2)

    def fncMainPage(self):
        # 로그인 페이지
        self.mainWidget.setCurrentIndex(0)

    def fncUserListPage(self):
        self.loginUserList.setColumnWidth(0, 390)
        print(client_list)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

