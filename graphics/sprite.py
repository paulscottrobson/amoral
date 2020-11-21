# *******************************************************************************************
# *******************************************************************************************
#
#       File:           sprite.py
#       Date:           21st November 2020
#       Purpose:        Sprite Conversion classes
#       Author:         Paul Robson (paul@robson.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

from PIL import Image												# PILLOW PREQREQUISITE

# *******************************************************************************************
#
#								16 colour sprite conversion class
#
# *******************************************************************************************

class SpriteConverter(object):
	def __init__(self):
		self.palette = self.getPalette()							# subclass for different palettes.
		assert len(self.palette) == 15 								# 15 colours + transparent.
	#
	#		Convert one sprite.
	#
	def convert(self,imageFile,width = 32,height = 32,alignment = None):
		alignment = alignment if alignment is not None else SpriteConverter.CENTRE
		image = Image.open(imageFile)								# load image
		image = self.preProcess(image,width,height,alignment)
		spriteData = [ 0 ] * (width*height>>1)						# allocate memory for it.
		for x in range(0,width):									# scan the image
			for y in range(0,height):
				rgba = image.getpixel((x,y))						# get RGBA
				if rgba[3] != 0: 									# if not transparent.
					col = self.getBestColour(rgba) 					# what colour fits best ?
																	# add into MSN/LSN.
					spriteData[y*(width >> 1)+(x>>1)] += (col if x%2 != 0 else (col << 4))
		return spriteData
	#
	#		Match RGBA colour against palette
	#
	def getBestColour(self,rgba):
		best = 99999999.0
		for i in range(0,len(self.palette)):
			score = pow(self.palette[i][0]-rgba[0],2)+pow(self.palette[i][1]-rgba[1],2)+pow(self.palette[i][2]-rgba[2],2)
			if score < best:
				col = i+1
				best = score
		return col

	#
	#		Convert a sprite to the given size, keeping the aspect ratio the same. If a sprite
	#		is not square it will be aligned accordingly.
	#
	def preProcess(self,image,width,height,alignment):
		return image

SpriteConverter.CENTRE = 'C'										# centred
SpriteConverter.CENTREBOTTOM = 'B'									# centred horizontally bottom vertically

# *******************************************************************************************
#
#					This is for the standard X16 Palette from the C64
#
# *******************************************************************************************

class StandardSpriteConverter(SpriteConverter):
	def getPalette(self):
		return [[255, 255, 255], [136, 0, 0], [170, 255, 238], [204, 68, 204], [0, 204, 85], [0, 0, 170], [238, 238, 119], [221, 136, 85], [102, 68, 0], [255, 119, 119], [51, 51, 51], [119, 119, 119], [170, 255, 102], [0, 136, 255], [187, 187, 187]]

# *******************************************************************************************
#
#					This is my 16 bit colour palette which isn't designed on 
#						the principle that all NTSC colours look like mud.
#
# *******************************************************************************************

class ImprovedSpriteConverter(SpriteConverter):
	def getPalette(self):
		palette = [[0, 0, 0], [255, 0, 0], [0, 255, 0], [255, 255, 0], [0, 0, 255], [255, 0, 255], [0, 255, 255], [255, 255, 255], [0, 0, 0], [87, 87, 87], [160, 160, 160], [255, 128, 0], [150, 70, 20], [128, 255, 0], [0, 128, 255], [255, 205, 243]]
		return palette[1:]


sc = ImprovedSpriteConverter()
spriteData = sc.convert("mario.png",64,64,SpriteConverter.CENTRE)
h = open("sprites.dat","w")
for c in spriteData:
	h.write("{0:02x}".format(c))
h.close()
