import matplotlib.pyplot as plt


def display_images(lefthand, righthand, titles=(None, None), asgray=(False, False)):
	"""
	Display two images side-by-side
	param: lefthand: the left-hand image
	param: righthand: the right-hand image
	param: titles: 2-tuple of string image titles
	param: asgray: 2-tuple of boolean grayscale flags to control image dislay
	return: None
	"""
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
	ax1.imshow(lefthand) if asgray[0] == False else ax1.imshow(lefthand, cmap="gray")
	if titles[0]: ax1.set_title(titles[0], fontsize=25)
	ax2.imshow(righthand) if asgray[1] == False else ax2.imshow(righthand, cmap="gray")
	if titles[1]: ax2.set_title(titles[1], fontsize=25)
	plt.show()


def display_image(image, title=None, asgray="auto"):
	"""
	Simple image dislay function
	param: image: the image to be displayed
	param: title: the title to be given (optional)
	param: asgray: whether the image should be should in grayscale (optional, default = auto)
					if auto, then if the number of color channels is one, grayscale is selected
	return: None
	"""
	as_gray = False
	if asgray == "auto":
		shape = image.shape
		if len(shape) < 3 or shape[-1] < 2:
			as_gray = True
	elif asgray == "gray":
		as_gray = True
	fig, ax = plt.subplots(1, 1, figsize=(30,20))
	ax.imshow(image) if as_gray == False else ax.imshow(image, cmap="gray")
	if title: ax.set_title(title, fontsize=25)
	plt.show()