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
		else:
			# Holds all the currently used object IDs (some may have disappeared)
			objectIDs = list(self.objects.keys())
			object_centroids = list(self.objects.values())
			object_centroidsarray = np.array(object_centroids)
			
			# Calculate distances between each centroid
			distance = dist.cdist(np.array(object_centroids), input_centroids)
			print("distance array:\n", distance, "\n")
			
			# Gets the index of the shortest distance in each row and then orders them in ascending order.
			# Each entry represents the index of input centroid with the shortest distance to the corresponding
			# (already) tracked centroid
			distance_min_row = distance.min(axis=1).argsort()
			print("index of sorted distance array:\n", distance_min_row)
			
			# Do the same for the columns
			distance_min_col = distance.argmin(axis=1)[distance_min_row]
			print("sorted distance columns:\n", distance_min_col)
			
			# Essentially x,y coords for the minimum values (1 per row)
			min_coords = list(zip(distance_min_row, distance_min_col))
			print("Coordinates of minimum value:\n", min_coords)
			
			# Holds the used x and y  coords so that the same centroid isn't used twice
			usedX = set()
			usedY = set()
			
			# Go through each row coord and assign objects[row] with with a new coordinate (the input centroid)
			for (x, y) in min_coords:
				if (x not in usedX) and (y not in usedY):
				
					print("Modifying row", x)
					# Replace the existing centroid with the new input centroid with smallest distance
					self.objects[objectIDs[x]] = input_centroids[y]
					# Reset the disappeared time
					self.disappearedTime[objectIDs[x]] = 0
			
					# Add x and y to the used sets
					usedX.add(x)
					usedY.add(y)
					# TODO add maximum distance a centroid can move between a frame
			
			# TODO if there's more x remaining, treat these as having disappeared
			
			# TODO if there's more y remaining, register as new objects
			
			print(len(usedX), len(objectIDs))
			print(len(usedY), len(input_centroids))