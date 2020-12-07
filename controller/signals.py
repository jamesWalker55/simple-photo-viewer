# ===HOW TO USE THIS===

# import this to create new signals:
#     from controller.signals import *

# then use this to create signals
#     controller.signals.SIGNAL_NAME = BoolSignal()

# it is preferred if you defined this first:
#     self.signals = self.controller.signals
# then you can do this:
#     self.signals.SIGNAL_NAME = BoolSignal()



# just Signal(bool) doesn't work
# instead, use this.
# You'll need to do 
#   variable.signal.emit(True) 
# instead of 
#   variable.emit(True)


from PySide2.QtCore import Signal, QObject

class BoolSignal(QObject):
	signal = Signal(bool)

class StringSignal(QObject):
	signal = Signal(str)

class IntegerSignal(QObject):
	signal = Signal(int)