class Body:
	def __init__(self, id, location):
		# History of the body's  locations [x,y] of centroid
		self.visited = []
		# Current location of the body
		self.location = location
		self.ID = id
		# Represents the current direction of the body (0 is out of train) (out is down the screen)
		self.direction = 0
	
	# Test function
	def print_something(self):
		print("Hello, made it into the body")
	
	# Determine the direction (based on overall movement across frame)
	def determine_direction(self):
		# go through each of the locations
		total = 0
		for i in self.visited:
			total += i[1]
		average = total / len(self.visited)
		print("average:", average)
		print("locationNow:", self.location[1])
		if average < self.location[1]:
			# Less than current location (moving down)
			self.direction = 0
			print("direction is 0")
		else:
			self.direction = 1
			print("direction is 1")
	
	# Update the location of the body
	def update_location(self, location):
		# Set its current location
		self.location = location
		# Add the location to the history
		self.visited.append(location)
		self.determine_direction()
	
	# Also determine the direction (should have more than 1 location when this is called
	
	# Return boolean, if line is crossed. True if line has been crossed. Requires y coord of line.
	def line_crossed(self, line_y):
		# If the direction is out (down)
		if self.direction == 0:
			# check if y coord is less than lineY (therefore line has been crossed)
			if line_y > self.location[1]:
				return True
			else:
				return False
		
		# If the line is in (up)
		if self.direction == 1:
			# check if y coord is more than lineY (therefore line has been crossed)
			if line_y > self.location[1]:
				return True
			else:
				return False
