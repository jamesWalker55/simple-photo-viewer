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
