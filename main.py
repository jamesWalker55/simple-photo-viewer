# So far I only did the model and controller
# I didn't touch the view AT ALL. It's incompatible with the current code

import sys
from PySide2.QtWidgets import QApplication

import view.mainwindow 
import controller.controller 
import model.memory

memory = model.memory.MainMemory()
controller = controller.controller.Controller(memory)

app = QApplication(sys.argv)
mw = view.mainwindow.MainWindow(controller)
mw.show()
sys.exit(app.exec_())
