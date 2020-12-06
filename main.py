# So far I only did the model and controller
# I didn't touch the view AT ALL. It's incompatible with the current code

from pathlib import Path

import sys
from PySide2.QtWidgets import QApplication

import view.mainwindow 
from controller.io import *
import model.memory

memory = model.memory.MainMemory()

app = QApplication(sys.argv)
mw = view.mainwindow.MainWindow(memory)
mw.show()
sys.exit(app.exec_())
