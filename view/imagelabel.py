from PySide2.QtWidgets import QScrollArea, QLabel
from PySide2.QtCore import QPointF, QSize
from PySide2.QtGui import QPalette, Qt, QPixmap, QCursor,QImage

from pathlib import Path

class ImageLabel(QLabel):
	def __init__(self):
		super(ImageLabel, self).__init__()
		# stretch image to label
		self.setScaledContents(True)
		self.resize(1,1)
		
	@property
	def originalSize(self):
		if self.pixmap() == None:
			return QSize(0,0)
		return self.pixmap().size()

	# pass in a Path object
	def setImage(self, image):
		self.setPixmap(QPixmap.fromImage(QImage(str(image))))

	def qsizeResize(self, qsize):
		self.resize(qsize)

	# # unused, use qsizeResize for better precision
	# def factorResize(self, factor):
	# 	self.resize(self.originalSize * factor)


