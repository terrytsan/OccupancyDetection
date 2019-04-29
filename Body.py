class Body:
	def __init__(self, id, location):
		# History of the body's  locations [x,y] of centroid
		self.visited = []
		# Current location of the body
		self.location = location
		self.ID = id
		# Represents the current direction of the body (0 is out of train) (out is down the screen)
		self.direction = 0
		
		self.crossedLine = False
		# Flag indicates if the body has crossed the line
		
	# Determine the direction (based on overall movement across frame)
	def determine_direction(self):
		# go through each of the locations
		total = 0
		for i in self.visited:
			total += i[1]
		# Calculate the average of all past locations
		average = total / len(self.visited)
		if average < self.location[1]:
			# Less than current location (moving down)
			self.direction = 0
		else:
			self.direction = 1
	
	# Update the location of the body
	def update_location(self, location):
		# Set its current location
		self.location = location
		# Add the location to the history
		self.visited.append(location)
		self.determine_direction()
		

