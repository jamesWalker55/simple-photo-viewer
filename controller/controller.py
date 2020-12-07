import os
from random import shuffle

class Controller:

	def __init__(self, memory):
		self.memory = memory

	# ===================== IMAGE =====================
	# Sets memory's image to the given path
	def imageOpen(self, path):
		# You only need to define image path and sort
		# Everything ese is auto-defined
		if not path.is_file():
			print(path)
			raise FileNotFoundError("File path is invalid.")

		# set image to path
		self.memory.image = path

		# Break if current list is same folder as previous
		if self.memory.tempimagelist:
			if self.memory.tempimagelist[1].parent == self.memory.folder:
				return

		self.createTempImageList()

	# Sets memory's image to next or previous image
	def imageNext(self, index):
		imglist = self.memory.tempimagelist
		currentIndex = imglist.index(self.memory.image)
		newIndex = (currentIndex+index) % len(imglist)
		imageOpen(self.memory, imglist[newIndex])

	# ===================== SORT =====================
	# Sets memory's sort settings
	def setFolderSort(self, sort, reverse=False):
		# Allowed sorts: name, cdate, mdate, size, 
		self.memory.sort = sort
		self.memory.sortReverse = reverse
		createTempImageList()

	# Gets memory's sort settings
	def getFolderSort(self):
		return self.memory.sort , self.memory.sortReverse

	# ===================== IMAGE LIST =====================
	# Creates a temp image list from memory.imagelist
	# This considers the sortReverse variable
	def createTempImageList(self):
		# Allowed sorts: name, cdate, mdate, size, 
		sortfunct = None
		sort = self.memory.sort

		if sort == "random":
			paths = list(self.memory.imagelist)
			shuffle(paths)
			self.memory.tempimagelist = paths

		else:
			if sort == "name":
				sortfunct = lambda p: p.name
			elif sort == "cdate":
				sortfunct = os.path.getctime
			elif sort == "mdate":
				sortfunct = os.path.getmtime
			elif sort == "size":
				sortfunct = os.path.getsize
			else:
				# uses name sort by default
				print("createTempImageList: self.memory.sort is invalid! Defaulting to name.")
				sortfunct = lambda p: p.name

			self.memory.tempimagelist = sorted(
				self.memory.imagelist, 
				key=sortfunct, 
				reverse=self.memory.sortReverse
				)
