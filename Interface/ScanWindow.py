import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from DateTimeDialog import DateTimeDialog
from StartScanDialog import StartScanDialog

from Scanner.connect import dantem_login
from Scanner.connect import scan_and_accept
from Scanner.connect import scan_and_report
import pyautogui as pag
import requests

from threading import Timer
from threading import Thread
import sys


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(LoginWindow, self).__init__(*args, **kwargs)
        self.width = 250
        self.height = 130
        self.setFixedWidth(250)
        self.setFixedHeight(130)
        self.setWindowTitle("Přihlášení")

        self.main_window = ScanWindow(parent=self)

        layout = LoginLayout(parent=self)
        self.setLayout(layout)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        sys.exit()


class LoginLayout(QtWidgets.QGridLayout):
    def __init__(self, parent):
        self.parent = parent
        super(LoginLayout, self).__init__()
        self.setSpacing(10)

        self.username_label = QtWidgets.QLabel("ID:")
        self.username_input = QtWidgets.QLineEdit()
        self.password_label = QtWidgets.QLabel("Heslo:")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Přihlásit do DAPu")
        self.login_button.setMinimumWidth(160)
        self.login_button.clicked.connect(self.login_clicked)

        self.addWidget(self.username_label, 1, 0, 1, 1,
                       alignment=QtCore.Qt.AlignRight)
        self.addWidget(self.username_input, 1, 1, 1, 3,
                       alignment=QtCore.Qt.AlignLeft)
        self.addWidget(self.password_label, 2, 0, 1, 1,
                       alignment=QtCore.Qt.AlignRight)
        self.addWidget(self.password_input, 2, 1, 1, 3,
                       alignment=QtCore.Qt.AlignLeft)
        self.addWidget(self.login_button, 3, 0, 1, 4,
                       alignment=QtCore.Qt.AlignCenter)


    def login_clicked(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.username_input.clear()
        self.password_input.clear()
        session = dantem_login(username, password)
        self.parent.main_window.session = session
        self.parent.main_window.username = username
        self.parent.main_window.show()
        self.parent.hide()


class ScanWindow(QtWidgets.QMainWindow):
    username_changed = QtCore.pyqtSignal(object)
    session_started = QtCore.pyqtSignal(object)

    def __init__(self, parent, *args, **kwargs):
        super(ScanWindow, self).__init__(*args, **kwargs)
        self.width = 500
        self.height = 500
        self.setFixedWidth(500)
        self.setFixedHeight(500)
        self.setWindowTitle("Tržiště")

        self._username = ""
        self._session = None
        self._dates = []
        self.dates_string = ""
        self.accept = True
        self.parent = parent

        self.layout = ScanLayout(parent=self)
        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.timer = RepeatedTimer(interval=5.0,
                                   function=None,
                                   scan_window=self)
        self.timer.start()
        self.timer.stop()


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.timer.stop()
        sys.exit()


    @property
    def session(self):
        return self._session


    @session.setter
    def session(self, value: requests.session):
        self._session = value
        self.session_started.emit(value)


    @property
    def dates(self):
        return self._dates


    @dates.setter
    def dates(self, value: list):
        self._dates = value


    @property
    def username(self):
        return self._username


    @username.setter
    def username(self, value):
        self._username = value
        self.username_changed.emit(value)


class ScanLayout(QtWidgets.QGridLayout, QtCore.QObject):
    def __init__(self, parent):
        self.parent = parent
        super(ScanLayout, self).__init__()
        self.setSpacing(15)

        font_1 = QtGui.QFont("Segoe", 11)
        font_1.setWeight(75)
        font_1.setLetterSpacing(QtGui.QFont.PercentageSpacing, 100)
        font_1.setCapitalization(QtGui.QFont.AllUppercase)

        font_2 = QtGui.QFont("Segoe", 11)
        font_2.setWeight(75)
        font_2.setLetterSpacing(QtGui.QFont.PercentageSpacing, 100)
        font_2.setCapitalization(QtGui.QFont.AllUppercase)

        font_3 = QtGui.QFont("Segoe", 14)
        font_3.setWeight(75)
        font_3.setLetterSpacing(QtGui.QFont.PercentageSpacing, 105)
        font_3.setCapitalization(QtGui.QFont.AllUppercase)

        logged_label = QtWidgets.QLabel("Přihlášen/a jako:")
        self.addWidget(logged_label, 2, 1, 1, 1,
                       alignment=QtCore.Qt.AlignRight)

        self.logged_username = QtWidgets.QLabel("")
        self.parent.username_changed.connect(self.username_display)
        self.addWidget(self.logged_username, 2, 2, 1, 1)

        log_out_button = QtWidgets.QPushButton("Odhlásit")
        log_out_button.clicked.connect(self.logout_clicked)
        self.addWidget(log_out_button, 2, 3, 1, 2)

        set_datetime_options_button = QtWidgets.QPushButton("Časové možnosti")
        set_datetime_options_button.setFont(font_1)
        set_datetime_options_button.setFixedHeight(50)
        set_datetime_options_button.clicked.connect(
            self.datetime_options_clicked)
        self.addWidget(set_datetime_options_button, 3, 1, 1, 4)

        start_scan_button = QtWidgets.QPushButton("Zahájit scan")
        start_scan_button.setStyleSheet("background-color: lightgreen")
        start_scan_button.setFont(font_3)
        start_scan_button.setFixedHeight(50)
        start_scan_button.clicked.connect(self.start_scan_dialog)
        self.addWidget(start_scan_button, 5, 1, 1, 2)

        stop_scan_button = QtWidgets.QPushButton("Ukončit scan")
        stop_scan_button.setStyleSheet("background-color: orangered")
        stop_scan_button.setFont(font_3)
        stop_scan_button.setFixedHeight(50)
        stop_scan_button.clicked.connect(self.stop_scan)
        self.addWidget(stop_scan_button, 5, 3, 1, 2)

        self.status_updates = QtWidgets.QTextEdit()
        self.status_updates.setReadOnly(True)
        self.status_updates.append((str(self.parent)))
        self.parent.session_started.connect(self.post_session_info)
        self.addWidget(self.status_updates, 6, 1, 3, 4)


    def post_session_info(self, value: requests.Session):
        check_text = "Moje osobní karta"
        login_succes = "PŘIHLÁŠENÍ BYLO NEÚSPĚŠNÉ, ZKUS TO ZNOVU"
        if check_text in value.get("https://dap.dantem.net/employees/").text:
            login_succes = "Přihlášení proběhlo úspěšně!"
        headers = value.headers
        cookies = value.cookies
        login_window = str(self.parent.parent)
        post_text = f"**************\n"\
                    f"{login_window}\n"\
                    f"{headers}\n"\
                    f"{cookies}\n\n" \
                    f"{login_succes}\n**************"
        self.status_updates.append(post_text)


    def username_display(self, value: str):
        self.logged_username.setText(value)


    def logout_clicked(self):
        url = "https://dap.dantem.net/auth/login/"
        session = self.parent.session
        response = session.post(url, headers={'Connection': 'close'})
        headers = str(response.headers)
        if "'Connection': 'close'" in headers:
            self.status_updates.append("Spojení přerušeno")
            self.status_updates.clear()
            self.parent.hide()
            self.parent.parent.show()
        else:
            self.status_updates.append("ODHLÁŠENÍ NEÚSPĚŠNÉ! UKONČI PROGRAM")


    def datetime_options_clicked(self):
        datetime_dialog = DateTimeDialog(parent=self.parent)
        datetime_dialog.exec_()


    def start_scan_dialog(self):
        scan_dialog = StartScanDialog(self.parent)
        scan_dialog.exec_()


    def start_scan(self, interval: int):
        accept = self.parent.accept
        dates = self.parent.dates
        session = self.parent.session
        
        start_date = dates[0][0].strftime("%d.%m.%Y")
        end_date = dates[-1][1].strftime("%d.%m.%Y")
        
        timer = self.parent.timer
        timer.interval = interval
        timer.args = [session, start_date, end_date, dates, accept]
        timer.function = scan_and_accept
        timer.start()



    def stop_scan(self):
        timer = self.parent.timer
        timer.stop()
        self.status_updates.append("Scan přerušen!")


    @staticmethod
    def report_scan_results(report: str):
        def alert(text: str):
            pag.alert(text=text, title="Inventura přijata!")
        thread = Thread(target=alert(report))
        thread.start()


class RepeatedTimer(object):
    def __init__(self, interval, function, scan_window, *args, **kwargs):
        self.scan_window = scan_window
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False


    def _run(self):
        self.is_running = False
        self.start()
        ret = self.function(*self.args, **self.kwargs)
        self.scan_window.layout.status_updates.append(ret)
        if "Nabídka přijata" in ret:
            self.scan_window.layout.report_scan_results(ret)


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True


    def stop(self):
        self._timer.cancel()
        self.is_running = False
