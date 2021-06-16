import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5 import QtGui
from datetime import date
from datetime import datetime
import json
import os
from pathlib import Path


class DateTimeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(DateTimeDialog, self).__init__(*args, **kwargs)

        self.parent = parent

        self.width = 250
        self.height = 400
        self.setFixedWidth(250)
        self.setFixedHeight(400)
        self.setWindowTitle("Časové možnosti")

        layout = DateTimeLayout(parent=self, scan_window=self.parent)
        self.setLayout(layout)


class DateTimeLayout(QtWidgets.QGridLayout):
    def __init__(self, parent=None, scan_window=None):
        self.OPTIONS_FOLDER = Path(os.path.join(os.environ["USERPROFILE"],
                                                "Documents\\Dantem\\Options"))
        self.OPTIONS_FILE = Path(os.path.join(self.OPTIONS_FOLDER,
                                              "saved_options.json"))
        self.parent = parent
        self.scan_window = scan_window
        super(DateTimeLayout, self).__init__()
        self.setSpacing(10)

        self.start_date_edit = QtWidgets.QDateTimeEdit()
        self.start_date_edit.setMinimumHeight(25)
        self.start_date_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setMinimumDate(date.today())
        self.start_date_edit.dateTimeChanged.connect(
            self.set_date_time_on_change)
        self.addWidget(self.start_date_edit, 1, 1, 1, 4)

        self.end_date_edit = QtWidgets.QDateTimeEdit()
        self.end_date_edit.setMinimumHeight(25)
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setMinimumDate(date.today())
        self.addWidget(self.end_date_edit, 2, 1, 1, 4)

        self.add_datetime = QtWidgets.QPushButton("Přidat možnost")
        self.add_datetime.setMinimumWidth(230)
        self.add_datetime.setMinimumHeight(30)
        self.add_datetime.clicked.connect(self.add_date)
        self.addWidget(self.add_datetime, 3, 1, 1, 4,
                       alignment=QtCore.Qt.AlignCenter)

        self.del_last_option = QtWidgets.QPushButton("Smazat poslední")
        self.del_last_option.setMinimumWidth(110)
        self.del_last_option.setMinimumHeight(40)
        self.del_last_option.clicked.connect(self.del_last_date)
        self.addWidget(self.del_last_option, 4, 1, 1, 2,
                       alignment=QtCore.Qt.AlignCenter)

        self.del_all_options = QtWidgets.QPushButton("Smazat všechny")
        self.del_all_options.setMinimumWidth(110)
        self.del_all_options.setMinimumHeight(40)
        self.del_all_options.clicked.connect(self.del_all_dates)
        self.addWidget(self.del_all_options, 4, 3, 1, 2,
                       alignment=QtCore.Qt.AlignCenter)

        self.save_options_file = QtWidgets.QPushButton("Uložit pro příště")
        self.save_options_file.setMinimumWidth(110)
        self.save_options_file.setMinimumHeight(40)
        self.save_options_file.clicked.connect(self.save_dates_to_file)
        self.addWidget(self.save_options_file, 5, 1, 1, 2,
                       alignment=QtCore.Qt.AlignCenter)

        self.load_options_file = QtWidgets.QPushButton("Nahrát možnosti")
        self.load_options_file.setMinimumWidth(110)
        self.load_options_file.setMinimumHeight(40)
        self.load_options_file.clicked.connect(self.load_dates_from_file)
        self.addWidget(self.load_options_file, 5, 3, 1, 2,
                       alignment=QtCore.Qt.AlignCenter)

        self.dates_list = QtWidgets.QTextEdit()
        self.dates_list.setReadOnly(True)
        self.addWidget(self.dates_list, 6, 1, 3, 4)

        self.save_options = QtWidgets.QPushButton("Potvrdit časové možnosti")
        self.save_options.setMinimumWidth(230)
        self.save_options.clicked.connect(self.save_dates)
        self.addWidget(self.save_options, 9, 1, 1, 4,
                       alignment=QtCore.Qt.AlignCenter)


    def set_date_time_on_change(self, date_time):
        ref_date_time = self.end_date_edit.dateTime()
        if ref_date_time <= date_time:
            self.end_date_edit.setDateTime(date_time)


    def add_date(self):
        start_date = self.start_date_edit.dateTime().toPyDateTime()
        end_date = self.end_date_edit.dateTime().toPyDateTime()
        if start_date <= end_date:
            new_date = [start_date, end_date]
            self.scan_window.dates.append(new_date)
            self.dates_list.append(self.date_range_to_string(
                start_date, end_date))
        else:
            self.date_input_error(message="Chyba! Data musí jít po sobě...")


    def del_last_date(self):
        if self.scan_window.dates:
            self.dates_list.undo()
            self.scan_window.dates.pop()


    def del_all_dates(self):
        if self.scan_window.dates:
            self.dates_list.clear()
            self.scan_window.dates.clear()
            
            
    def check_saved_file_path(self):
        if not os.path.exists(self.OPTIONS_FILE):
            self.OPTIONS_FOLDER.mkdir(parents=True)
            with open(self.OPTIONS_FILE, "w") as f:
                f.write("{}")

                
    def save_dates_to_file(self):
        self.check_saved_file_path()
        dates_dict = {}
        dates = self.scan_window.dates
        date_index = 0
        for date_time in dates:
            dates_string = self.date_range_to_string(date_time[0], date_time[1])
            dates_dict[date_index] = dates_string
            date_index += 1

        with open(self.OPTIONS_FILE, "w") as f:
            json.dump(dates_dict, f)


    def load_dates_from_file(self):
        self.del_all_dates()
        self.check_saved_file_path()
        with open(self.OPTIONS_FILE, "r") as f:
            dates_dict = json.load(f)
        for date_time in dates_dict.values():
            date_pair = date_time.split(" - ")
            parsed_date_pair = []
            for d in date_pair:
                parsed_date_pair.append(
                    datetime.strptime(d, "%d.%m.%Y %H:%M"))
            self.scan_window.dates.append(parsed_date_pair)
            self.dates_list.append(date_time)


    def save_dates(self):
        dates = self.scan_window.dates
        dates_string = "\n"
        for date_time in dates:
            dates_string += self.date_range_to_string(
                date_time[0], date_time[1], newline=True)
        self.scan_window.layout.status_updates.append(dates_string)
        self.scan_window.dates_string = dates_string
        self.scan_window.layout.status_updates.append(
            "Časové možnosti úspěšně uloženy!\n")
        self.parent.close()


    @staticmethod
    def date_range_to_string(date_1, date_2, delimiter=" - ", newline=False):
        dates_string = (date_1.strftime("%d.%m.%Y %H:%M") + delimiter +
                        date_2.strftime("%d.%m.%Y %H:%M"))
        if newline:
            dates_string += "\n"
        return dates_string


    @staticmethod
    def date_input_error(message):
        date_error_dlg = DateErrorDialog(message=message)
        date_error_dlg.exec_()


class DateErrorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, message="", *args, **kwargs):
        super(DateErrorDialog, self).__init__(*args, **kwargs)

        self.parent = parent
        self.message = message

        self.width = 250
        self.height = 150
        self.setFixedWidth(250)
        self.setFixedHeight(150)
        self.setWindowTitle("CHYBA")

        grid = QtWidgets.QGridLayout()

        font_1 = QtGui.QFont("Segoe", 11)
        font_1.setWeight(75)
        font_1.setLetterSpacing(QtGui.QFont.PercentageSpacing, 100)


        error_message = QtWidgets.QLabel(self.message)
        error_message.setFont(font_1)
        grid.addWidget(error_message, 1, 1, alignment=QtCore.Qt.AlignCenter)

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self.ok_clicked)
        grid.addWidget(ok_button, 2, 1)

        layout = grid
        self.setLayout(layout)


    def ok_clicked(self):
        self.close()



