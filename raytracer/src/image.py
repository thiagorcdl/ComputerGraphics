# Image class for manipulating byte by byte
import math
import array
import sys

class Image:
	def __init__(self, w, h, path):
		size = w * h
		self.bytes = array.array('B', [0] * (w * h * 3))
		for i in range(size):
			self.bytes[i * 3 + 2] = 255
		self.w = w
		self.h = h
		self.path = path

	def paint(self, x, y, rgb):
		i = ((self.h - y - 1) * self.w + x) * 3
		self.bytes[i] = min(255, int(rgb.x * 255))
		self.bytes[i+1] = min(255, int(rgb.y * 255))
		self.bytes[i+2] = min(255, int(rgb.z * 255))
	
	def writeFile(self):
		with open(self.path, 'wb') as img:
			img.write('P6 %d %d 255\n' % (self.w, self.h))
			img.write(self.bytes.tostring())
