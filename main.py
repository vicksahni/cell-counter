import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import windows
import cellcounter

app = QApplication(sys.argv)

driver_window = windows.DriverWindow()
driver_window.run()

app.exec_()

