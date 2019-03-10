# This is used to test the ObjectTracker class
import cv2
import numpy as np
from ObjectTracker import ObjectTracker

obTrack = ObjectTracker()
# rectangles = []

rectangles = [[300, 200, 50, 50], [104, 190, 50, 50], [600, 300, 50, 50]]
objects = obTrack.update(rectangles)

rectangles = [[0, 220, 50, 50], [600, 320, 50, 50], [100, 230, 50, 50], [50, 50, 50, 50], [0, 0, 50, 50]]
objects = obTrack.update(rectangles)

for x, y in objects.items():
  print(x, y)