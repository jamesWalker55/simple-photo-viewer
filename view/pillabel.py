from PySide2.QtWidgets import QScrollArea, QLabel
from PySide2.QtCore import QPointF, QSize
from PySide2.QtGui import QPalette, Qt, QPixmap, QCursor,QImage

from PIL import Image
from lib.ImageQt import ImageQt
from pathlib import Path

class PILLabel(QLabel):
	def __init__(self):
		super(PILLabel, self).__init__()
		# stretch image to label
		self.setScaledContents(False)
		self.resize(1,1)
		self.image = None
		
	@property
	def originalSize(self):
		if self.image == None:
			return QSize(0,0)
		return QSize(*self.image.size)

	# pass in a Path object
	def setImage(self, path):
		# Need to convert, otherwise label will be corrupted
		# ImageQt won't work for RGB images for some reason
		self.image = Image.open(path).convert(mode = "RGBA")
		self.setPILImage(self.image)

	# sets an Image object to pixmap
	def setPILImage(self, image):
		qtimage = ImageQt(image)
		self.setPixmap(QPixmap.fromImage(QImage(qtimage)))

	def qsizeResize(self, qsize, zoomlevel):
		if not self.image:
			return
		# Resize image
		if zoomlevel >= 1:
			# zoom in
			resampleMode = Image.LANCZOS
		elif zoomlevel < 1:
			# zoom out
			resampleMode = Image.LANCZOS
		tempImage = self.image.resize(qsize.toTuple(), resample=resampleMode)
		self.setPILImage(tempImage)
		# Resize label
		self.resize(qsize)

	# # unused, use qsizeResize for better precision
	# def factorResize(self, factor):
	# 	self.resize(self.originalSize * factor)


