from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import sys
from pathlib import Path

# from view.imagelabel import ImageLabel
from view.pillabel import PILLabel
from view.zoomcanvas import ZoomCanvas

# To create new signals
from controller.signals import *

class MainWindow(QMainWindow):
	
	def __init__(self, controller, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setWindowIcon(QIcon("./res/photo-album.ico"))
		self.setWindowTitle("Photo Viewer")
		self.settings = QSettings("James", "Photo Viewer")

		self.controller = controller
		self.signals = controller.signals

		self.loadSettings()

		# Setup signals before label and zoom are created
		self.setupSignals()
		self.setupToolBar()

		# create imagelabel
		self.content = PILLabel()

		# create zoom canvas
		self.zoom = ZoomCanvas(self.content, self.controller)
		self.setCentralWidget(self.zoom)

	def setupToolBar(self):
		self.toolbar = QToolBar("Main Toolbar")
		self.toolbar.setObjectName("Main Toolbar")
		self.setBackgroundRole(QPalette.Base)
		self.toolbar.setIconSize(QSize(16,16))
		self.addToolBar(self.toolbar)
		self.toolbar.setMovable(False)

		self.act_open = QAction(QIcon(r"./res/folder-open-image.png"),"&Open image", self)
		self.act_open.setStatusTip("Open an image")
		self.act_open.triggered.connect( self.openImageDialog )
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
			self.act_sort[sort].triggered.connect(
					lambda _=None,a=sort: self.changeSortMethod(a)
					)
			# self.act_sort.append(self.act_sort[sort])
			self.sort_menu.addAction(self.act_sort[sort])

		self.act_sortListTool = QToolButton()
		self.act_sortListTool.setMenu(self.sort_menu)
		self.act_sortListTool.setPopupMode(QToolButton.MenuButtonPopup)
		self.act_sortListTool.triggered.connect(self.act_sortListTool.setDefaultAction)
		self.act_sortListTool.setDefaultAction(self.act_sort[self.controller.getFolderSort()[0]])
		self.toolbar.addWidget(self.act_sortListTool)

		self.act_reverseSort = QAction(QIcon(r"./res/book-open-previous.png"),"&Reverse image list", self)
		self.act_reverseSort.setStatusTip("Reverse the currently used image list")
		self.act_reverseSort.setCheckable(True)
		self.act_reverseSort.triggered.connect( 
				lambda s: self.changeSortReverse(s) 
				)
		self.act_reverseSort.setChecked(self.controller.getFolderSort()[1] or False)
		self.toolbar.addAction(self.act_reverseSort)

	def changeSortMethod(self, sort):
		self.controller.setFolderSort(sort)
		self.signals.updateTitle.signal.emit(True)

	def changeSortReverse(self, reverse):
		sort = self.controller.getFolderSort()[0]
		print(reverse)
		self.controller.setFolderSort(sort, reverse)
		self.signals.updateTitle.signal.emit(True)

	def setupSignals(self):
		self.signals.updateTitle = BoolSignal()
		self.signals.updateTitle.signal.connect(
			lambda e: self.updateWindowTitle()
		)

		self.signals.buttonFitImage = BoolSignal()
		self.signals.buttonFitImage.signal.connect(
			lambda e: self.act_fitWindow.setChecked(e)
		)

		self.signals.setFitImage = BoolSignal()
		self.signals.setFitImage.signal.connect(
			lambda e: self.act_fitWindow.setChecked(e)
		)

	# Opens a "open file" dialog, then passes on to self.openImage
	def openImageDialog(self, s):
		print("Toolbar: Open image")

		# "Open file" dialog
		filetypeList = " ".join(self.controller.supportedFileTypes())
		fname, _ = QFileDialog.getOpenFileName(
			self, 
			'Open file', 
			str(self.controller.getLastOpenFolder()),
			f"Image Files ({filetypeList})"
		)
		if not fname:  # if no file is opened
			print("openImageDialog: Nothing opened.")
			return

		# Set "lastOpenFolder" to the parent of file
		pathFname = Path(fname)
		self.controller.setLastOpenFolder(pathFname.parent)

		# Set image to image in memory
		self.controller.imageOpen(pathFname)
		# load image from memory
		self.openImage(self.controller.imagePath())

	def nextImage(self, index):
		print(f"Toolbar: Go next {index} image")
		if not self.controller.imagePath():
			print("nextImage: No image in memory, skipping.")
			return

		# move to next image in memory
		self.controller.imageNext(index)
		# load image from memory
		self.openImage(self.controller.imagePath())

	# The actual code for loading a new image
	def openImage(self, path):
		# Reload image label image
		self.content.setImage(path)
		# Set new window title
		self.updateWindowTitle()
		self.saveSettings()
		self.signals.buttonFitImage.signal.emit(True)
		self.signals.updateTitle.signal.emit(True)

	# Pass in true / false to set state
	# Called only when button is pressed
	def fitImage(self, checked):
		print(f"Toolbar: Fit image to view, state={checked}")
		# print(checked)
		if checked:
			self.signals.buttonFitImage.signal.emit(True)
			self.signals.updateTitle.signal.emit(True)
		else:
			self.signals.buttonFitImage.signal.emit(False)
			self.signals.updateTitle.signal.emit(True)

	# Updates title to match viewer information
	# path must be a Path object
	def updateWindowTitle(self):
		path = self.controller.imagePath()
		if not path:
			self.setWindowTitle(f"Photo Viewer")
			return
		filename = path.name
		zoomlevel = self.zoom.zoomLevel
		listlength = len(self.controller.getTempImageList())
		listindex = self.controller.getImageIndex() + 1
		titleString = f"Photo Viewer - [{listindex}/{listlength}] ({zoomlevel:.2f}x) {path.name}"
		self.setWindowTitle(titleString)

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
		if e.key() == Qt.Key_Comma:
			self.nextImage(-1)
		if e.key() == Qt.Key_Period:
			self.nextImage(1)
		super(MainWindow, self).keyPressEvent(e)

	# ===================== Save settings =====================
	def loadSettings(self):
		self.restoreGeometry(self.settings.value("geometry"))
		self.restoreState(self.settings.value("windowState"))
		lastPath = self.settings.value("memory/lastOpenFolder")
		self.controller.setLastOpenFolder( Path(lastPath) )

		sort = self.settings.value("memory/sort")
		sortReverse = self.settings.value("memory/sortReverse") == "true"
		self.controller.setFolderSort(sort, sortReverse)

	def closeEvent(self, e):
		self.saveSettings()
		super().closeEvent(e)

	def saveSettings(self):
		save = lambda name, value: self.settings.setValue(name, value)
		
		save("geometry", 
			self.saveGeometry() )
		save("windowState", 
			self.saveState() )
		save("memory/lastOpenFolder", 
			str( self.controller.getLastOpenFolder() ))
		save("memory/sort", 
			str(self.controller.getFolderSort()[0]))
		save("memory/sortReverse", 
			self.controller.getFolderSort()[1])
		print(self.controller.getFolderSort()[1])
		
		# self.settings.setValue("geometry", self.saveGeometry() )
		# self.settings.setValue("windowState", self.saveState() )
		# self.settings.setValue("memory/lastOpenFolder", str(self.memory.lastOpenFolder))
		# self.settings.setValue("memory/sort", str(self.memory.sort))
		# self.settings.setValue("memory/sortReverse", self.memory.sortReverse)
