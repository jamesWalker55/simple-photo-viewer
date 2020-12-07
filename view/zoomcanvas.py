# Displays an image using qlabel
# Scrollwheel for zooming
# Middle mouse for panning

# To use a widget in this, pass the widget as the `content`
# The widget must have the following functions:

# - self.content.originalSize
#     - returns unzoomed size of widget

# - self.content.qsizeResize(dimension)
#     - resizes widget with a given QSize instance

# - self.content.mapFromGlobal
#     - converts global to local point (all widgets should have this already)

from PySide2.QtWidgets import QScrollArea, QLabel
from PySide2.QtCore import QPointF, QSize, Signal, QObject
from PySide2.QtGui import QPalette, Qt, QPixmap, QCursor,QImage


class BoolSignal(QObject):
	signal = Signal(bool)


class ZoomCanvas(QScrollArea):
	def __init__(self, content, controller, *args, **kwargs):
		super(ZoomCanvas, self).__init__(*args, **kwargs)
		self.controller = controller
		self.signals = controller.signals

		self.setupSignals()

		self.zoomLevel = 1.0
		self.drag = None
		self.fitImage = True

		self.setBackgroundRole(QPalette.Dark)

		# aligns widget to center of area
		self.setAlignment(Qt.AlignCenter)

		self.content = content
		self.setWidget(self.content)

		self.buttonFitImage(True)

	def setupSignals(self):
		# This is triggered on pressing button and opening image only
		# zooming by scroll does NOT trigger this
		self.signals.buttonFitImage.signal.connect(
			lambda e: self.buttonFitImage(e)
		)
		self.signals.setFitImage.signal.connect(
			lambda e: self.setFitImage(e)
		)

	def setFitImage(self, state):
		print(f"FitImage set to {state}")
		self.fitImage = state

	# ===================== Zoom Functions =====================
	# Zooming with mouse wheel
	# Unrelated to fitImage
	# Also adjusts scroll position
	def scrollZoom(self, factor):
		print("zooming by scrolling")
		if self.fitImage:
			self.signals.setFitImage.signal.emit(False)

		# don't do anything if mouse is dragging
		if self.drag:
			return

		# constants for calculating scroll position after zoom
		globalPoint = QCursor.pos()
		ix, iy = self.content.mapFromGlobal(globalPoint).toTuple()
		ex, ey = self.mapFromGlobal(globalPoint).toTuple()
		previousZoomLevel = self.zoomLevel

		# Zoom in label
		self.zoomLevel *= factor
		if self.zoomLevel > 3:
			self.zoomLevel = 3
		elif self.zoomLevel < 1/3:
			self.zoomLevel = 1/3
		self.resizeContentToZoomLevel()

		# Calculate actual factor used
		realFactor = self.zoomLevel / previousZoomLevel

		# Adjust scroll according to mouse position
		if realFactor != 1.0:
			mx = ix*realFactor - ex + 1
			my = iy*realFactor - ey + 1
			self.setScrollPosition(mx, my)

		self.signals.updateTitle.signal.emit(True)
	
	# constantly called on window resize AND when fitimage is true
	# resizes image to window
	def zoomFitSize(self):
		print("fitting image to window")
		img_size = self.content.originalSize
		window_size = self.size() - QSize(2,2)

		if (img_size.width()<window_size.width()) and (img_size.height()<window_size.height()):
			self.zoomLevel = 1
			self.resizeContentToZoomLevel()
		else:
			# Ratio: w/h
			# > 0, it is wide
			# < 0, it is tall
			ratio = lambda size: size.width()/size.height()
			if ratio(img_size) >= ratio(window_size):
				# img wider than window
				self.zoomLevel = window_size.width() / img_size.width()
			elif ratio(img_size) < ratio(window_size):
				# img wider than window
				self.zoomLevel = window_size.height() / img_size.height()
			self.resizeContentToZoomLevel()

	# Resets zoom level to 1
	def zoomReset(self):
		print("setting zoom to 1")
		if self.zoomLevel != 1:
			self.zoomLevel = 1.0
			self.resizeContentToZoomLevel()

	# resizes content to zoom level
	def resizeContentToZoomLevel(self):
		# print("resizeContentToZoomLevel called")
		dimension = self.zoomLevel * self.content.originalSize
		self.content.qsizeResize(dimension)

	# Called when button is pressed
	def buttonFitImage(self, state):
		assert type(state) == bool

		# This is just `self.fitImage = state`
		self.signals.setFitImage.signal.emit(state)

		if self.fitImage:
			self.zoomFitSize()
			print("buttonFitImage: Fit to window")
		else:
			self.zoomReset()
			print("buttonFitImage: Set zoom to 1")

	# ===================== Useful Functions =====================
	def setScrollPosition(self, x, y):
		self.horizontalScrollBar().setValue(x)
		self.verticalScrollBar().setValue(y)

	def getScrollPosition(self):
		point = QPointF(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
		return point

	# ===================== EVENTS =====================

	# ===================== Wheel to Zoom =====================
	def wheelEvent(self, e):
		# Define scroll action to zoom
		scrollDelta = e.angleDelta().y()
		if scrollDelta>0:
			self.scrollZoom(1.25)
		elif scrollDelta<0:
			self.scrollZoom(0.8)

	# ===================== Panning =====================
	def mousePressEvent(self, e):
		# Start Panning
		if e.button() == Qt.MouseButton.MiddleButton:
			print("Panning: Started!")

			self.drag = {}
			self.drag["scrollbarPos"] = self.getScrollPosition()
			self.drag["scrollOrigin"] = e.localPos()
		super().mousePressEvent(e)

	def mouseMoveEvent(self, e):
		# Process Panning
		if self.drag:
			# requires:
			# e event
			# drag dictionary:
				# scrollbarPos, scrollOrigin
			difference = (e.localPos() - self.drag["scrollOrigin"])
			final = self.drag["scrollbarPos"] - difference
			final = final.toTuple()
			self.setScrollPosition(*final)
		super().mouseMoveEvent(e)

	def mouseReleaseEvent(self, e):
		# End Panning
		if e.button() == Qt.MouseButton.MiddleButton:
			# Remove drag dictionary
			# So drag evaluates to boolean(None) == False
			self.drag = None
			print("Panning: Released!")
		super().mouseReleaseEvent(e)

	# ===================== other events =====================
	# when window size changes...
	def resizeEvent(self, e):
		if self.fitImage:
			self.zoomFitSize()

		super().resizeEvent(e)

	# Define shortcuts
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_E:
			print(self.fitImage)
		# if e.key() == Qt.Key_Q:
		# 	self.toggleZoomFit()

		super(ZoomCanvas, self).keyPressEvent(e)

