class Body:
	def __init__(self, id):
		# History of the body's  locations
		self.visited = []
		self.location = []
		self.ID = id
	
	# Adds a location to the body's history
	def add_location(self, location):
		self.visited.append(location)
	
	# Update the location of the body
	def update_location(self, location):
		self.location = location
		self.add_location(location)
