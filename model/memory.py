from PIL import Image

class MainMemory:
	def __init__(self):
		self._image = None
		# Allowed sorts: name, cdate, mdate, size, 
		self.sort = "name"
		# Allowed state: True, False
		self.sortReverse = False
		self.tempimagelist = None
		self.lastOpenFolder = None
		self.filetypes = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp")

	@property
	def imagelist(self):
		filelist = []
		for ftype in self.filetypes:
			filelist.extend(self.folder.glob(ftype))
		return filelist

	@property
	def folder(self):
		return self.image.parent

	@property
	def image(self):
		# .image property
		return self._image

	@image.setter
	def image(self, value):
		self._image = value
		# self.PILimage