from scipy.spatial import distance as dist
import numpy as np


class ObjectTracker():
	def __init__(self):
		# initialise variables when object is first created
		self.currentObjectID = 0
		self.objects = {}
		self.disappearedTime = {}
	
	# Add the centroid to the list of objects to track
	def start_track(self, centroid):
		self.objects[self.currentObjectID] = centroid
		self.disappearedTime[self.currentObjectID] = 0
		self.currentObjectID = self.currentObjectID + 1
	
	# Stop tracking the passed in object
	def end_track(self, objectID):
		# Remove both instances of the object from the dictionaries
		del self.objects[objectID]
		del self.disappearedTime[objectID]
	
	# Updates the list of tracked objects, pass in current frames's rectangles
	def update(self, rectangles):
		# Just testing how I can pass in the centroids as a parameter
		# print(len(rectangles))
		# for i in rectangles:
		# print(i)
		
		# initialize array to hold all the centroids for the inputted rectangles
		input_centroids = np.zeros((len(rectangles), 2), dtype="int")
		
		# Extract the centroid from every input rectangle
		for (rec, (startX, startY, endX, endY)) in enumerate(rectangles):
			# print("new", startX, startY, endX, endY)
			# place in an array
			x_centroid = int((startX + endX) / 2)
			y_centroid = int((startY + endY) / 2)
			input_centroids[rec] = (x_centroid, y_centroid)
		
		# If there are currently no tracked objects
		if len(self.objects) == 0:
			print("No objects, adding", len(rectangles))
			for centroid in input_centroids:
				# Start tracking all inputted rectangles
				self.start_track(centroid)
		
		object_centroids = list(self.objects.values())
		
		# Calculate distances between each centroid
		distance = dist.cdist(np.array(object_centroids), input_centroids)
		
		for d in distance:
			print("distance", d)
