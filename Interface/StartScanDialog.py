import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


class StartScanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(StartScanDialog, self).__init__(*args, **kwargs)

        self.parent = parent

        self.width = 250
        self.height = 250
        self.setFixedWidth(250)
        self.setFixedHeight(250)
        self.setWindowTitle("Zahájit scan")

        layout = StartScanLayout(parent=self, scan_window=self.parent)
        self.setLayout(layout)


class StartScanLayout(QtWidgets.QGridLayout):
    def __init__(self, parent=None, scan_window=None):
        super(StartScanLayout, self).__init__()
        self.parent = parent
        self.scan_window = scan_window
        self.setSpacing(10)

        font = QtGui.QFont("Segoe", 12)
        font.setWeight(75)
        font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 105)
        font.setCapitalization(QtGui.QFont.AllUppercase)

        self.time_interval_label = QtWidgets.QLabel(
            "Časový interval (vteřiny):")
        self.addWidget(self.time_interval_label, 1, 1, 1, 3,
                       alignment=QtCore.Qt.AlignLeft)

        self.time_interval_setting = QtWidgets.QSpinBox()
        self.time_interval_setting.setMinimum(1)
        self.time_interval_setting.setMinimumHeight(25)
        self.addWidget(self.time_interval_setting, 1, 4, 1, 1)

        # TODO: make this work
        self.auto_accept_label = QtWidgets.QLabel(
            "Automaticky přijímat inventury?")
        self.addWidget(self.auto_accept_label, 2, 1, 1, 3,
                       alignment=QtCore.Qt.AlignLeft)

        self.auto_accept_setting = QtWidgets.QCheckBox()
        self.addWidget(self.auto_accept_setting, 2, 4, 1, 1)

        self.dates_list = QtWidgets.QTextEdit()
        self.dates_list.setReadOnly(True)
        self.dates_list.append("Moje časové možnosti:")
        self.dates_list.append(self.scan_window.dates_string)
        self.addWidget(self.dates_list, 3, 1, 2, 4)

        self.start_scan_button = QtWidgets.QPushButton("ZAHÁJIT SCAN")
        self.start_scan_button.setStyleSheet("background-color: lightgreen")
        self.start_scan_button.setFont(font)
        self.start_scan_button.setMinimumWidth(230)
        self.start_scan_button.setMinimumHeight(40)
        self.start_scan_button.clicked.connect(self.start_scan_button_clicked)
        self.addWidget(self.start_scan_button, 5, 1, 1, 4,
                       alignment=QtCore.Qt.AlignCenter)


    def start_scan_button_clicked(self):
        interval = self.time_interval_setting.value()
        accept_shifts = self.auto_accept_setting.isChecked()
        self.scan_window.accept = accept_shifts
        self.scan_window.layout.status_updates.append(
            f"Automaticky přijímat inventury  -  {accept_shifts}")
        self.scan_window.layout.start_scan(interval=interval)
        self.close_parent()


    def close_parent(self):
        self.parent.close()



