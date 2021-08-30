from PyQt5.QtWidgets import QApplication
from ScanWindow import LoginWindow

import sys

def main():
    app = QApplication([])
    LoginWindow().exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()














