import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class AcceptDialog(QtWidgets.QDialog):
    def __init__(self):
        super(AcceptDialog, self).__init__()
        # self.report = report

        self.width = 250
        self.height = 150
        self.setWindowTitle("Inventura přijata!")

        # grid = AcceptLayout(parent=self)
        # self.setLayout(grid)


# class AcceptLayout(QtWidgets.QGridLayout):
#     def __init__(self, parent=None):
#         super(AcceptLayout, self).__init__()
#         self.parent = parent
#         error_message = QtWidgets.QLabel("Mrdat")
#         self.addWidget(error_message, 1, 1, alignment=QtCore.Qt.AlignCenter)
#
#         ok_button = QtWidgets.QPushButton("OK")
#         # ok_button.clicked.connect(self.ok_clicked_accept)
#         self.addWidget(ok_button, 2, 1)


    # def ok_clicked_accept(self):
    #     self.parent.close()




