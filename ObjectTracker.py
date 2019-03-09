# An object tracker keeps track of rectangles it is given, assigning unique IDs to each one
from scipy.spatial import distance as dist
import numpy as np


class ObjectTracker():
	def __init__(self):
		# initialise variables when object is first created
		self.currentObjectID = 0
		# Dictionary which holds the centroid for each object
		self.objects = {}
		# Holds the amount of frames a corresponding object has been "missing" for
		self.disappearedTime = {}
		# Maximum time an object can go "missing" for before tracking ends
		self.maxDisTime = 10
	
	# Add the centroid to the list of objects to track
	def start_track(self, centroid):
		self.objects[self.currentObjectID] = centroid
		print("Registered", centroid)
		self.disappearedTime[self.currentObjectID] = 0
		self.currentObjectID = self.currentObjectID + 1
	
	# Stop tracking the passed in object
	def end_track(self, objectID):
		# Remove both instances of the object from the dictionaries
		del self.objects[objectID]
		del self.disappearedTime[objectID]
	
	# Updates the list of tracked objects, pass in current frames's rectangles
	def update(self, rectangles):
		# The maximum distance an object can move between frames
		max_dist = 100
		
		print("Length of input", len(rectangles))
		if len(rectangles) == 0:
			# If nothing is input, increment disappeared time of all objects
			print("Nothing input")
			for objectID in list(self.objects.keys()):
				self.disappearedTime[objectID] += 1
				if self.disappearedTime[objectID] > self.maxDisTime:
					self.end_track(objectID)
			# Leave the function
			return self.objects
			
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
		else:
			# Holds all the currently used object IDs (some may have disappeared)
			objectIDs = list(self.objects.keys())
			object_centroids = list(self.objects.values())
			
			# Calculate distances between each centroid
			distance = dist.cdist(np.array(object_centroids), input_centroids)
			print("distance array:\n", distance, "\n")
			
			# Gets the index of the shortest distance in each row and then orders them in ascending order.
			# Each entry represents the index of input centroid with the shortest distance to the corresponding
			# (already) tracked centroid
			distance_min_row = distance.min(axis=1).argsort()
			
			# Do the same for the columns
			distance_min_col = distance.argmin(axis=1)[distance_min_row]
			
			# Essentially x,y coords for the minimum values (1 per row)
			min_coords = list(zip(distance_min_row, distance_min_col))
			
			# Holds all possible indexes of objects and input_Centroids so that the same centroid isn't used twice
			remaining_x = set(list(range(0, len(objectIDs))))
			remaining_y = set(list(range(0, len(input_centroids))))
			
			# Go through each row coord and assign objects[row] with with a new coordinate (the input centroid)
			for (x, y) in min_coords:
				if (x in remaining_x) and (y in remaining_y):
					# print("Distance between", x, "and", y, "is", distance[x][y])
					if distance[x][y] < max_dist:
						# print("Distance acceptable")
						# Replace the existing centroid with the new input centroid with smallest distance
						self.objects[objectIDs[x]] = input_centroids[y]
						# Reset the disappeared time
						self.disappearedTime[objectIDs[x]] = 0
						
						# Remove x and y from remaining set
						remaining_x.remove(x)
						remaining_y.remove(y)
			
			# Go through all the remaining original objects (no match has been found in this new frame)
			for x in remaining_x:
				# Increment disappeared time
				self.disappearedTime[objectIDs[x]] += 1
				# Check if time value has exceeded limit
				print(self.objects[objectIDs[x]], "Has disappeared")
				if self.disappearedTime[objectIDs[x]] > self.maxDisTime:
					self.end_track(objectIDs[x])
			
			# Go through the remaining input centroids that weren't matched and register them as new objects
			for y in remaining_y:
				self.start_track(input_centroids[y])
		
		# return the dictionary of tracked objects
		return self.objects
