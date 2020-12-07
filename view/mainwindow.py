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
		self.loadSettings()

		self.imagelabel = ImageLabel()

		self.zoom = ZoomCanvas(self.imagelabel)
		self.setCentralWidget(self.zoom)
		self.setupToolBar()

		self.zoom.fitImageSignal.signal.connect(self.setFitWindowState)
		self.zoom.updateTitleSignal.signal.connect(lambda e: self.setTitleToPath(self.memory.image))

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

		self.act_sort = {}
		self.sort_menu = QMenu()
		for sort in ("name", "cdate", "mdate", "size", "random"):
			self.act_sort[sort] = QAction(QIcon(fr"./res/sortIcons/{sort}.png"),f"&Sort by {sort}", self)
			self.act_sort[sort].setStatusTip(f"Sorts filelist by {sort}")
			self.act_sort[sort].triggered.connect( lambda _="fuck",a=sort: self.setSort(a) )
			# self.act_sort.append(self.act_sort[sort])
			self.sort_menu.addAction(self.act_sort[sort])

		self.act_sortListTool = QToolButton()
		self.act_sortListTool.setMenu(self.sort_menu)
		self.act_sortListTool.setPopupMode(QToolButton.MenuButtonPopup)
		self.act_sortListTool.triggered.connect(self.act_sortListTool.setDefaultAction)
		self.act_sortListTool.setDefaultAction(self.act_sort[self.memory.sort])
		self.toolbar.addWidget(self.act_sortListTool)

		self.act_reverseSort = QAction(QIcon(r"./res/book-open-previous.png"),"&Reverse image list", self)
		self.act_reverseSort.setStatusTip("Reverse the currently used image list")
		self.act_reverseSort.setCheckable(True)
		self.act_reverseSort.triggered.connect( lambda s: self.setSortReverse() )
		self.act_reverseSort.setChecked(self.memory.sortReverse or False)
		self.toolbar.addAction(self.act_reverseSort)


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

	def setSort(self, sort):
		print(f"setSort: Set sort mode to \"{sort}\"")
		self.memory.sort = sort
		if self.memory.image:
			controller.io.createTempImageList(self.memory)

	def setSortReverse(self):
		self.memory.sortReverse = not self.memory.sortReverse
		self.zoom.updateTitleSignal.signal.emit(True)


	def setFitWindowState(self, boolean):
		self.act_fitWindow.setChecked(boolean)

	def setTitleToPath(self, path):
		if not path:
			self.setWindowTitle(f"Photo Viewer")
			return
		filename = path.name
		zoomlevel = self.zoom.zoomLevel
		listlength = len(self.memory.tempimagelist)
		listindex = self.memory.tempimagelist.index(self.memory.image)+1
		self.setWindowTitle(f"Photo Viewer - [{listindex}/{listlength}] {path.name} ({zoomlevel:.2f}x)")

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
	def loadSettings(self):
		self.restoreGeometry(self.settings.value("geometry"))
		self.restoreState(self.settings.value("windowState"))
		lastPath = self.settings.value("memory/lastOpenFolder")
		self.memory.lastOpenFolder = Path(lastPath)
		self.memory.sort = self.settings.value("memory/sort")
		self.memory.sortReverse = bool(self.settings.value("memory/sortReverse"))

	def closeEvent(self, e):
		self.saveSettings()
		super().closeEvent(e)

	def saveSettings(self):
		self.settings.setValue("geometry", self.saveGeometry() )
		self.settings.setValue("windowState", self.saveState() )
		self.settings.setValue("memory/lastOpenFolder", str(self.memory.lastOpenFolder))
		self.settings.setValue("memory/sort", str(self.memory.sort))
		self.settings.setValue("memory/sortReverse", self.memory.sortReverse)
