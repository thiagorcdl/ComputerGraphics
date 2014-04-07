# Objects present on the scene
import math
from vector import *

class Sphere:
	def __init__(self,xyz,rgb,radius,material):
		self.pos = xyz		# Position (x,y,z)
		self.col = rgb		# Color (r,g,b)
		self.rad = radius	# Sphere size
		self.mat = material	# 0 for reflective, 1 for transparent

class Plane:
	def __init__(self,xyz,rgb,material):
		self.pos = xyz		# Position (x,y,z)
		self.col = rgb		# Color (r,g,b)
		self.mat = material	# 0 for reflective, 1 for transparent

class Light:
	def __init__(self,xyz,rgb,intenst):
		self.pos = xyz		# Position (x,y,z)
		self.col = rgb		# Color (r,g,b)
		self.int = intenst	# Light intensity
		self.rad = 0.5

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Ray:
	def __init__(self,pos, direction):
		self.pos = pos
		direction.normalize()
		self.dir = direction

	def distance(self,point):
		return math.sqrt((point - self.pos).sqlength())

	def intersect(self,obj):
		if obj.__class__.__name__ == "Plane":
			d = float((obj.pos.y - self.pos.y))/(self.dir.y)
			if d <= 0:
				return [False,]
			point = self.pos + self.dir*d
			normal = Vector(0,1,0)
			return [True,d,point,normal]
		elif obj.__class__.__name__ == "Sphere": 
			# Based on lab
			l = obj.pos - self.pos
			s = l.dot(self.dir)
			if s < 0:
				return [False,]
			r = obj.rad
			r2 = r**2
			m2 = l.dot(l) - s**2
			if m2 > r2:
				return [False,]
			q = math.sqrt(r2-m2)
			t = s-q
			if t < 0:
				t = s+q
			point = self.pos + self.dir*t
			normal = point - obj.pos
			return [True,t,point,normal]
		else:
			return[False,]
