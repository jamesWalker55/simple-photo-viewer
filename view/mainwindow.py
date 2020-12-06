from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import sys
from pathlib import Path

from view.imagelabel import ImageLabel
from view.zoomcanvas import ZoomCanvas
import controller.io

class MainWindow(QMainWindow):
	"""docstring for MainWindow"""
	def __init__(self, memory, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setWindowIcon(QIcon("./res/photo-album.ico"))
		self.setWindowTitle("Photo Viewer")
		self.settings = QSettings("James", "Photo Viewer")
		# self.resize(800, 600)
		self.memory = memory
		self.readSettings()

		self.imagelabel = ImageLabel()

		self.zoom = ZoomCanvas(self.imagelabel)
		self.setCentralWidget(self.zoom)
		self.setupToolBar()

		self.zoom.fitImageSignal.signal.connect(self.setFitWindowState)

	def setupToolBar(self):
		self.toolbar = QToolBar("Main Toolbar")
		self.setBackgroundRole(QPalette.Base)
		self.toolbar.setIconSize(QSize(16,16))
		self.addToolBar(self.toolbar)
		self.toolbar.setMovable(False)

		self.act_open = QAction(QIcon(r"./res/folder-open-image.png"),"&Open image", self)
		self.act_open.setStatusTip("Open an image")
		self.act_open.triggered.connect( self.openImage )
		self.toolbar.addAction(self.act_open)

		self.act_prev = QAction(QIcon(r"./res/arrow-180.png"),"&Previous image", self)
		self.act_prev.setStatusTip("Load previous image in folder")
		self.act_prev.triggered.connect( lambda: self.nextImage(-1) )
		self.toolbar.addAction(self.act_prev)

		self.act_next = QAction(QIcon(r"./res/arrow.png"),"&Next image", self)
		self.act_next.setStatusTip("Load next image in folder")
		self.act_next.triggered.connect( lambda: self.nextImage(1) )
		self.toolbar.addAction(self.act_next)

		self.act_fitWindow = QAction(QIcon(r"./res/magnifier-zoom-fit.png"),"&Fit image", self)
		self.act_fitWindow.setStatusTip("Fit image to window size")
		self.act_fitWindow.setCheckable(True)
		self.act_fitWindow.setChecked(True)
		self.act_fitWindow.triggered.connect( lambda s: self.fitImage(s) )
		self.toolbar.addAction(self.act_fitWindow)

	def openImage(self, s):
		print("Toolbar: Open image")
		filetypeList = " ".join(self.memory.filetypes)
		fname, _ = QFileDialog.getOpenFileName(
			self, 
			'Open file', 
			str(self.memory.lastOpenFolder),
			f"Image Files ({filetypeList})")
		if not fname:
			print("openImage: Nothing opened.")
			return
		pathedFname = Path(fname)
		self.memory.lastOpenFolder = pathedFname.parent
		controller.io.imageOpen(self.memory, pathedFname)
		self.imagelabel.setImage(self.memory.image)
		self.setTitleToPath(self.memory.image)
		self.zoom.zoomFitSize()
		self.saveSettings()

	def nextImage(self, index):
		print(f"Toolbar: Go next {index} image")
		print(self.memory.image)
		if not self.memory.image:
			print("nextImage: No image in memory, skipping.")
			return
		controller.io.imageNext(self.memory, index)
		self.imagelabel.setImage(self.memory.image)
		self.setTitleToPath(self.memory.image)
		self.zoom.zoomFitSize()
		self.saveSettings()

	def fitImage(self, s):
		print(f"Toolbar: Fit image to view, state={s}")
		self.zoom.toggleZoomFit()
		if self.zoom.fitImage:
			self.act_fitWindow.setChecked(True)
		elif not self.zoom.fitImage:
			self.act_fitWindow.setChecked(False)

	def setFitWindowState(self, boolean):
		self.act_fitWindow.setChecked(boolean)

	def setTitleToPath(self, path):
		self.setWindowTitle(f"Photo Viewer - {path.name}")

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
		if e.key() == Qt.Key_Comma:
			self.nextImage(-1)
		if e.key() == Qt.Key_Period:
			self.nextImage(1)
		# if e.key() == Qt.Key_Left:
		# 	self.nextImage(-1)
		# if e.key() == Qt.Key_Right:
		# 	self.nextImage(1)
		if e.key() == Qt.Key_A:
			print(self.memory.image)
			print(self.memory.lastOpenFolder)
		super(MainWindow, self).keyPressEvent(e)

	# ===================== Save settings =====================
	def readSettings(self):
		self.restoreGeometry(self.settings.value("geometry"))
		self.restoreState(self.settings.value("windowState"))
		lastPath = self.settings.value("memory/lastOpenFolder")
		self.memory.lastOpenFolder = Path(lastPath)

	def closeEvent(self, e):
		self.saveSettings()
		super().closeEvent(e)

	def saveSettings(self):
		self.settings.setValue("geometry", self.saveGeometry() )
		self.settings.setValue("windowState", self.saveState() )
		self.settings.setValue("memory/lastOpenFolder", str(self.memory.lastOpenFolder))
