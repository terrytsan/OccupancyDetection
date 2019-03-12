# This is used to test the ObjectTracker class
import cv2
import numpy as np
from BodyTracker import BodyTracker

obTrack = BodyTracker()
# rectangles = []

rectangles = [[300, 200, 50, 50], [104, 190, 50, 50], [600, 300, 50, 50]]
objects = obTrack.update(rectangles)

rectangles = [[0, 220, 50, 50], [600, 320, 50, 50], [100, 230, 50, 50], [50, 50, 50, 50], [0, 0, 50, 50]]
objects = obTrack.update(rectangles)

# x is the ID and y is the body (an class instance)
for x, y in objects.items():
	print("Return of Body Tracker:", x, y.location)
