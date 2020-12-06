import os

def imageOpen(memory, path):
	# You only need to define image path and sort
	# Everything ese is auto-defined
	if not path.is_file():
		print(path)
		raise FileNotFoundError("File path is invalid.")
	memory.image = path
	createTempImageList(memory)

# Go to next or previous image
def imageNext(memory, index):
	imglist = memory.tempimagelist
	currentIndex = imglist.index(memory.image)
	newIndex = (currentIndex+index) % len(imglist)
	imageOpen(memory, imglist[newIndex])

def setFolderSort(memory, sort, reverse=False):
	# Allowed sorts: name, cdate, mdate, size, 
	memory.sort = sort
	memory.sortReverse = reverse
	createTempImageList(memory)

def createTempImageList(memory):
	# Allowed sorts: name, cdate, mdate, size, 
	sortfunct = None
	if memory.sort == "name":
		sortfunct = lambda p: p.name
	elif memory.sort == "cdate":
		sortfunct = os.path.getctime
	elif memory.sort == "mdate":
		sortfunct = os.path.getmtime
	elif memory.sort == "size":
		sortfunct = os.path.getsize
	else:
		# uses name sort by default
		print("createTempImageList: memory.sort is invalid! Defaulting to name.")
		sortfunct = lambda p: p.name

	paths = sorted(
		memory.imagelist, 
		key=sortfunct, 
		reverse=memory.sortReverse
		)
	memory.tempimagelist = paths
