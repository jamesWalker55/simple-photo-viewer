from PIL import Image

class MainMemory:
	def __init__(self):
		self._image = None
		# Allowed sorts: name, cdate, mdate, size, random
		self.sort = "random"
		# Allowed state: True, False
		self.sortReverse = False
		self.tempimagelist = None
		self.lastOpenFolder = None
		self.filetypes = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp")

	# memory.imagelist
	@property
	def imagelist(self):
		filelist = []
		for ftype in self.filetypes:
			filelist.extend(self.folder.glob(ftype))
		return filelist

	# memory.folder
	@property
	def folder(self):
		return self.image.parent

	# memory.image
	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, path):
		self._image = path