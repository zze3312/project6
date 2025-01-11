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
now_room_serial = ''
ADMIN_CODE = 'admin'

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("채팅창")
        self.mainWidget.setCurrentIndex(0)
        self.loginBtn.clicked.connect(self.login)
        self.inputNick.returnPressed.connect(self.login)
        self.adminBtn.clicked.connect(self.wordMngOpen)
        self.createChatPopBtn.clicked.connect(self.createChatPop)
        self.createChatBtn.clicked.connect(self.createChat)
        self.newChatTitle.returnPressed.connect(self.createChat)
        self.inputAdminCode.returnPressed.connect(self.loginAdmin)
        self.createChatPopCloseBtn.clicked.connect(self.createChatPopClose)
        self.reloadUserList.clicked.connect(self.userListPage)
        self.reloadChatList.clicked.connect(self.chatListPage)
        self.chatList.cellDoubleClicked.connect(self.enterChat)
        self.quitBtn.clicked.connect(self.quit)
        self.chatMsg.returnPressed.connect(self.sendMsg)
        self.sendBtn.clicked.connect(self.sendMsg)
        self.submitWord.clicked.connect(self.addWord)
        self.inputWord.returnPressed.connect(self.addWord)
        self.wordMngPopCloseBtn.clicked.connect(self.wordMngClose)
        self.wordList.cellDoubleClicked.connect(self.removeWord)
        self.newChatPopup.setHidden(True)
        self.wordMngPop.setHidden(True)
        self.roomInfoPop.setHidden(True)
        self.roomInfoOpenBtn.clicked.connect(self.roomInfoPopOpen)
        self.roomInfoCloseBtn.clicked.connect(self.roomInfoPopClose)

        self.chatMsg.setDisabled(True)

    def roomInfoPopOpen(self):
        global client_socket, now_room_serial
        room_info = client.getRoomInfo(client_socket, now_room_serial)
        self.roomInfoPop.setHidden(False)

    def roomInfoPopClose(self):
        self.roomInfoPop.setHidden(True)

    def wordMngClose(self):
        self.adminWidget.setCurrentIndex(0)
        self.wordMngPop.setHidden(True)

    def wordMngOpen(self):
        self.inputAdminCode.setText('')
        self.inputAdminCode.setFocus()
        self.wordMngPop.setHidden(False)

    def addWord(self):
        global client_socket
        input_word = self.inputWord.text()
        word_list = client.reqAddWord(input_word)
        self.inputWord.setText('')
        self.wordList.clear()
        self.wordList.setColumnWidth(0, 100)
        self.wordList.setColumnWidth(1, 230)
        rowCnt = len(word_list)
        self.wordList.setRowCount(rowCnt)

        if rowCnt > 0:
            for row in range(rowCnt):
                data = str(word_list[row]['seq'])
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.wordList.setItem(row, 0, item)

                data = word_list[row]['word']
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.wordList.setItem(row, 1, item)

    def removeWord(self, row, col):
        data = self.wordList.item(row, 0)
        word_list = client.reqRemoveWord(data.text())

        self.wordList.clear()
        self.wordList.setColumnWidth(0, 90)
        self.wordList.setColumnWidth(1, 230)
        rowCnt = len(word_list)
        self.wordList.setRowCount(rowCnt)

        if rowCnt > 0:
            for row in range(rowCnt):
                data = str(word_list[row]['seq'])
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.wordList.setItem(row, 0, item)

                data = word_list[row]['word']
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.wordList.setItem(row, 1, item)

    def loginAdmin(self):
        input_code = self.inputAdminCode.text()

        if input_code == ADMIN_CODE:
            self.adminWidget.setCurrentIndex(1)
            word_list = client.reqListWord()
            self.wordList.clear()
            self.wordList.setColumnWidth(0, 100)
            self.wordList.setColumnWidth(1, 210)
            rowCnt = len(word_list)
            self.wordList.setRowCount(rowCnt)

            if rowCnt > 0:
                for row in range(rowCnt):
                    data = str(word_list[row]['seq'])
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.wordList.setItem(row, 0, item)

                    data = word_list[row]['word']
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.wordList.setItem(row, 1, item)
        else:
            QMessageBox.information(self, "알림", "관리코드가 틀렸습니다.")

    def login(self):
        input_text = self.inputNick.text()

        if not input_text:
            QMessageBox.information(self, "알림", "닉네임을 입력해주세요.")
        else :
            # 서버에 접속
            global client_socket
            client_socket = client.connectClient(self)
            # 접속 후 메인화면으로 이동
            self.mainWidget.setCurrentIndex(1)

            self.userListPage()
            self.chatListPage()

    def mainPage(self):
        # 로그인 페이지
        self.mainWidget.setCurrentIndex(0)

    def userListPage(self):
        global client_socket
        self.loginUserList.setColumnWidth(0, 970)
        login_list = client.getUserList(client_socket)
        print(login_list)

        rowCnt = len(login_list)
        self.loginUserList.setRowCount(rowCnt)

        for row in range(rowCnt):
            login_user = login_list[row]['user'] + '(' + login_list[row]['user_ip'] + ')'

            item = QTableWidgetItem(login_user)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.loginUserList.setItem(row, 0, item)

    def chatListPage(self):
        global client_socket
        # 970
        self.chatList.setColumnWidth(0, 140)
        self.chatList.setColumnWidth(1, 500)
        self.chatList.setColumnWidth(2, 200)
        self.chatList.setColumnWidth(3, 110)
        chat_list = client.getChatList(client_socket)

        print(type(chat_list))
        rowCnt = len(chat_list)
        self.chatList.setRowCount(rowCnt)

        for row in range(rowCnt):
            data = chat_list[row]['serial']
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.chatList.setItem(row, 0, item)

            data = chat_list[row]['room_name']
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.chatList.setItem(row, 1, item)

            data = chat_list[row]['owner']
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.chatList.setItem(row, 2, item)

            data = str(chat_list[row]['now_cnt']) + ' / ' + str(chat_list[row]['max_cnt'])
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.chatList.setItem(row, 3, item)

    def createChatPop(self):
        self.newChatPopup.setHidden(False)
        self.newChatTitle.setFocus()

    def createChatPopClose(self):
        self.newChatTitle.setText('')
        self.newChatMemCnt.setValue(0)
        self.newChatPopup.setHidden(True)

    def createChat(self):
        global client_socket
        client.reqCreateChatRoom(self, client_socket)
        self.newChatTitle.setText('')
        self.newChatMemCnt.setValue(0)
        self.newChatPopup.setHidden(True)

        self.chatListPage()

    def enterChat(self, row, col):
        global now_room_serial
        data = self.chatList.item(row, 0)

        now_room_serial = client.reqConnectChat(self, client_socket, data.text())
        if now_room_serial != '':
            self.mainWidget.setCurrentIndex(2)
            self.chatMsg.setText('')
            self.chatMsgList.clear()
            self.chatMsg.setDisabled(False)
        else:
            QMessageBox.information(self, "알림", "방이 가득찼습니다.")


    def sendMsg(self):
        global client_socket, now_room_serial
        msg = self.chatMsg.text()
        client.sendMsg(client_socket, msg, now_room_serial)
        self.chatMsg.setText('')

    def quit(self):
        global client_socket, now_room_serial
        msg = 'quit'
        client.sendMsg(client_socket, msg, now_room_serial)
        now_room_serial = ''
        self.chatMsg.setText('')
        self.chatMsgList.clear()
        self.mainWidget.setCurrentIndex(1)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()


