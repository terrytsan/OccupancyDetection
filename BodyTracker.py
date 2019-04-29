# A body tracker keeps track of a set of rectangles it is given, assigning unique IDs to each one
# update the tracker with some new rectangles and it will return a dictionary of bodies
from scipy.spatial import distance as dist
import numpy as np
from Body import Body
import logging
# Logging configuration
logger = logging.getLogger(__name__)


class BodyTracker:
	def __init__(self):
		# initialise variables when the tracker is first created
		self.currentBodyID = 0
		# Dictionary which holds body objects (holding ID makes things easier) (might be able to change to array in future)
		self.bodies = {}
		# Dictionary holding the amount of frames a corresponding body has been "missing" for.
		self.disappearedTime = {}
		# Maximum time a body can go "missing" for before tracking ends
		self.maxDisTime = 10
		# The maximum distance a body can move between frames
		self.max_dist = 150
		
		logger.info("hello")
	
	# Create a body with the centroid and start tracking it
	def start_track(self, centroid):
		# Create a new body object
		body = Body(self.currentBodyID, centroid)
		# Add the new body to the list of bodies
		self.bodies[self.currentBodyID] = body
		
		logger.info(f"Registered {self.bodies[self.currentBodyID].location} as {self.bodies[self.currentBodyID].ID}")
		# Initialise a disappearedTime for the new body
		self.disappearedTime[self.currentBodyID] = 0
		# Increment the ID
		self.currentBodyID = self.currentBodyID + 1
	
	# Stop tracking the passed in body
	def end_track(self, body_id):
		# Remove both instances of the body from the dictionaries
		del self.bodies[body_id]
		del self.disappearedTime[body_id]
	
	# Updates the list of tracked bodies, pass in current frames's rectangles
	def update(self, rectangles):
		# print("Length of input", len(rectangles))
		if len(rectangles) == 0:
			# If nothing is input, increment disappeared time of all objects
			# print("Nothing input")
			for bodyID in list(self.bodies.keys()):
				self.disappearedTime[bodyID] += 1
				if self.disappearedTime[bodyID] > self.maxDisTime:
					self.end_track(bodyID)
			# Leave the function
			return self.bodies
			
		# initialize array to hold all the centroids for the inputted rectangles
		input_centroids = np.zeros((len(rectangles), 2), dtype="int")
		
		# Convert the inputted rectangles to centroids
		for (rec, (startX, startY, endX, endY)) in enumerate(rectangles):
			# print("new", startX, startY, endX, endY)
			x_centroid = int((startX + endX) / 2)
			y_centroid = int((startY + endY) / 2)
			input_centroids[rec] = (x_centroid, y_centroid)
		
		# If there are currently no tracked objects
		if len(self.bodies) == 0:
			# print("No objects, adding", len(rectangles))
			for centroid in input_centroids:
				# Start tracking all inputted rectangles
				self.start_track(centroid)
		else:
			# Try and approximate the new centroids to the tracked bodies (based on distance)
			# Holds all the currently used object IDs (some may have disappeared)
			body_ids = list(self.bodies.keys())
			
			existing_centroids = []
			for body in self.bodies.values():
				existing_centroids.append(body.location)
			
			# Calculate distances between each centroid
			distance = dist.cdist(np.array(existing_centroids), input_centroids)
			#print("distance array:\n", distance, "\n")
			
			# Gets the index of the shortest distance in each row and then orders them in ascending order.
			# Each entry represents the index of input centroid with the shortest distance to the corresponding
			# (already) tracked centroid
			distance_min_row = distance.min(axis=1).argsort()
			
			# Do the same for the columns
			distance_min_col = distance.argmin(axis=1)[distance_min_row]
			
			# List of x,y coords (in matrix) for the minimum values (1 per row)
			min_coords = list(zip(distance_min_row, distance_min_col))
			
			# Holds all possible indexes of objects and input_Centroids so that the same centroid isn't used twice
			remaining_x = set(list(range(0, len(body_ids))))
			remaining_y = set(list(range(0, len(input_centroids))))
			
			# Go through each row coord and assign bodies[row] with with a new coordinate (the input centroid)
			for (x, y) in min_coords:
				if (x in remaining_x) and (y in remaining_y):
					# print("Distance between", x, "and", y, "is", distance[x][y])
					if distance[x][y] < self.max_dist:
						# Replace the existing centroid with the new input centroid with smallest distance
						self.bodies[body_ids[x]].update_location(input_centroids[y])
						# Reset the disappeared time
						self.disappearedTime[body_ids[x]] = 0
						
						# Remove x and y from remaining set
						remaining_x.remove(x)
						remaining_y.remove(y)
			
			# Go through all the remaining original objects (no match has been found in this new frame)
			for x in remaining_x:
				# Increment disappeared time
				self.disappearedTime[body_ids[x]] += 1
				# Check if time value has exceeded limit
				logging.info(f"{self.bodies[body_ids[x]].location} {self.bodies[body_ids[x]].ID}. time till disapeared: {self.disappearedTime[body_ids[x]]}")
				if self.disappearedTime[body_ids[x]] > self.maxDisTime:
					logging.info(f"{self.bodies[body_ids[x]].location} {self.bodies[body_ids[x]].ID} has disappeared")
					self.end_track(body_ids[x])
			
			# Go through the remaining input centroids that weren't matched and register them as new objects
			for y in remaining_y:
				self.start_track(input_centroids[y])
		
		# return the dictionary of tracked objects
		return self.bodies
