#!/usr/bin/python
import sys
import math
import time
import random

from image import *
from objects import *
from vector import *

class Scene:
	def __init__(self,nRay):
		size = 0.5
		self.w = int(1280*size)	# Scene width
		self.h = int(728*size)	# Scene height
		self.fov = 0.5			# FoV
		self.bg = Vector(1,1,1)	# Background color (r,g,b)
		self.nray = nRay		# Amount of Rays in the scene
		self.lgt = []			# Array of Light sources
		self.sph = []			# Array of Spheres
		# Reads Spheres
		nSphere = int(raw_input("Enter the amount of spheres:"))
		for s in range(nSphere):
			print "\n# Sphere %d:" % (s+1,)
			x = float(raw_input("x: "))
			y = float(raw_input("y: "))
			z = float(raw_input("z: "))
			r = float(raw_input("Red: "))
			g = float(raw_input("Green: "))
			b = float(raw_input("Blue: "))
			rad = float(raw_input("Radius: "))
			mat = int(raw_input("material (0-reflect,1-transparent): "))
			self.sph.append(Sphere(Vector(x,y,z),[r,g,b],rad,mat))
		# Reads lights
		nLight = int(raw_input("Enter the amount of light sources:"))
		print "%d lights" % nLight
		for l in range(nLight):
			print "\n# Light %d:" % (l+1,)
			x = float(raw_input("x: "))
			y = float(raw_input("y: "))
			z = float(raw_input("z: "))
			r = float(raw_input("Red: "))
			g = float(raw_input("Green: "))
			b = float(raw_input("Blue: "))
			i = float(raw_input("Intensity: "))
			i2 = float(raw_input("Intensity:"))
			self.lgt.append(Light(Vector(x,y,z),[r,g,b],[i,i2]))
		# Sets floor
		self.flr = Plane( Vector(0,-5,0),[1,1,1],0)

	# Defines ray based on FOV 
	def createRay(self,x,y):
		ratio = float(self.w)/self.h
		# Projects coordinates into screen range (-1 to 1)
		x += 0.5
		y += 0.5
		xw = ((float(x)/self.w)*2 -1)
		yw = (float(y)/self.h)*2 -1
		# Projects into world view
		xw *= self.fov * ratio
		yw *= self.fov
		# Ray starting point: (0,0,0)
		return Ray(Vector(0,0,0),Vector(xw,yw,-1))

	# Executes raytracing and writes image file
	def renderScene(self,):
		image = Image(self.w,self.h,'raytrace.ppm')
		for j in range(self.h):
			for i in range(self.w):
				ray = self.createRay(i,j)
				color = self.trace(ray,0)
				image.paint(i,j,color)
		image.writeFile()
		print "\nFile written"

	# Checks for intersection with objects and calculates color
	def trace(self,ray, depth):
		hit = 0
		lastHit = sys.float_info.max	# Infinity
		nHit = Vector(0,0,0)
		pHit = Vector(0,0,0)
		# Hits spheres
		for i in range(len(self.sph)):
			intersection = ray.intersect(self.sph[i])
			if intersection[0] and intersection[1] < lastHit:
				hit = 1
				lastHit = intersection[1]
				pHit = intersection[2]
				nHit = intersection[3]
				obj = self.sph[i]
		# Hits floor
		intersection = ray.intersect(self.flr)
		if intersection[0] and intersection[1] < lastHit:
			hit = 1
			lastHit = intersection[1]
			pHit = intersection[2]
			nHit = intersection[3]
			obj = self.flr
		# Hits light source
		for i in range(len(self.lgt)):
			intersection = ray.intersect(self.lgt[i])
			if intersection[0] and intersection[1] < lastHit:
				hit = 2
				lastHit = intersection[1]
				pHit = intersection[2]
				nHit = intersection[3]
				obj = self.lgt[i]
		if hit == 0:
			return self.bg
		# Fix normal in case it is inversed
		if ray.dir.dot(nHit) > 0:
			nHit *= -1
		nHit.normalize()
		# Retrieves color
		nOffset = nHit * 0.02
		reflection = Vector(0,0,0)
		if hit ==1: # Uses Fresnel Effect
			hitAngle = ray.dir.dot(nHit)
			specular = 0.3
			fresnel = specular + (1-specular) * ((1+min(hitAngle,0))**5)
			if depth < self.nray and (obj.mat == 0 or obj.mat == 1): # Reflective obj
				reflRay = Ray(pHit + nOffset,ray.dir - nHit*2*hitAngle)
				reflection = self.trace(reflRay,depth+1) * fresnel
			refraction = Vector(0,0,0)
			if depth < self.nray and obj.mat == 1: # Translucid obj
				offs = 1/1.1
				intens = 0.7
				refrRay = Ray(pHit - nOffset,ray.dir*offs - nHit*(offs*hitAngle + math.sqrt(1-(offs**2)*(1- hitAngle**2))))
				refraction = self.trace(refrRay, depth+1) * intens * (1-fresnel)
			color = reflection + refraction
			color.x *= obj.col[0]
			color.y *= obj.col[1]
			color.z *= obj.col[2]
		elif hit == 2:	# No reflection/refraction
			# Calculate diffusion or shadow for each light
			for i in range(len(self.lgt)):
				lightDir = self.lgt[i].pos - pHit
				lightDir.normalize()
				nDotL = nHit.dot(lightDir)
				nDotL = max(0,nDotL)
				shadow = False
				lightRay = Ray(pHit + nOffset,lightDir)
				intersects = lightRay.intersect(self.flr)
				if intersects[0]:
					shadow = True
				else: # Checks if there is Object in front of it
					for j in range(len(self.sph)):
						intersects = lightRay.intersect(self.sph[j])
						if intersects[0]:
							shadow = True
							break
				if shadow:		# Shadows will be plain black
					continue
				print "light"
				c1 = self.lgt[i].col[0] * self.lgt[i].int[0] * obj.col[0]
				c2 = self.lgt[i].col[1] * self.lgt[i].int[0] * obj.col[1]
				c3 = self.lgt[i].col[2] * self.lgt[i].int[0] * obj.col[2]
				color += Vector(c1, c2, c3) * nDotL * self.lgt[i].int[1]
		return color

if __name__ == '__main__':
	# If number or Rays is not passed, 3 is used as default.
	sys.setrecursionlimit(2**16)
	try:
		nRay = int(sys.argv[1])
	except:
		nRay = 3
	# Reads the Scene and then renders the image
	scene = Scene(nRay)
	scene.renderScene()

