import cv2
import numpy as np
from BodyTracker import BodyTracker
from Body import Body

# constants
video = "example_01.mp4"
videoScaleFactor = 1
# minimum size of rectangles before they are shown
minRecSize = 3000
# y coord of the crossing line
line_y = 150

# Create an object tracker object
obTrack = BodyTracker()

# Number of people on the train
onTrain = 0


# Return boolean, if line is crossed. True if line has been crossed. Requires y coord of line.
def line_crossed(body_y, direction):
	# If the direction is out (down)
	if direction == 0:
		# check if y coord is less than lineY (therefore line has been crossed)
		if line_y > body_y:
			return True
		else:
			return False
	
	# If the line is in (up)
	if direction == 1:
		# check if y coord is more than lineY (therefore line has been crossed)
		if line_y < body_y:
			return True
		else:
			return False


# Draws a bounding box around each contour (of a minimum area) and show on the input image
def draw_graphics(contours, image):
	# holds all the rectangles (to be passed into the object tracker)
	rectangles = []
	rect_count = 0
	for c in contours:
		# Approximate a bounding rectangle around the contour
		x, y, w, h = cv2.boundingRect(c)
		# Only draw rectangles larger than minimumRecSize
		if (w * h) > minRecSize:
			rect_count = rect_count + 1
			# draw the rectangle on the passed in image
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
			rectangles.append([x, y, x + w, y + h])
			# Print the size of the rectangle next to the rectangle
			cv2.putText(image, str(w * h), (x - 1, y - 1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
	# Get a list of tracked objects
	tracked_bodies = obTrack.update(rectangles)
	
	# Draw the crossing line
	cv2.line(image, (0, line_y), (500, line_y), (0, 255, 0), 3)
	
	# Write text on the centroid
	for (ID, body) in tracked_bodies.items():
		body_x = body.location[0]
		body_y = body.location[1]
		# 0 is down
		if body.direction == 0:
			direction = "down"
		else:
			direction = "up"
			
		if line_crossed(body_y, body.direction):
			cv2.putText(image, "line crossed", (100, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
			
		trackedObjectText = ("ID: %s %s" % (ID, direction))
		cv2.putText(image, (trackedObjectText), (body_x - 10, body_y - 10),
					cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
		# rectangle indicating centroid
		cv2.rectangle(image, (body_x, body_y - 1), (body_x + 1, body_y + 1), (0, 255, 0), 2)
	# Print out the number of rectangles found
	cv2.putText(image, str(rect_count), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))


# Finds contours in given input image
def find_contours(input_image):
	# Find contours
	contours, hierarchy = cv2.findContours(input_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# Draw contours
	drawing = np.zeros((input_image.shape[0], input_image.shape[1], 3), dtype=np.uint8)
	color = (256, 0, 250)
	cv2.drawContours(drawing, contours, -1, color, cv2.LINE_4)
	# Draw bounding rectangles
	draw_graphics(contours, drawing)
	return drawing


# Load the video
cap = cv2.VideoCapture(video)

# want to detect shadows so they can be thresholded
subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=20, detectShadows=1)
subtractorTwo = cv2.createBackgroundSubtractorKNN()

# This kernel will be used with the background subtractor
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))

# Play the video
while 1:
	ret, frame = cap.read()
	if not ret:
		break
	
	# resize frame
	frame = cv2.resize(frame, (0, 0), fx=videoScaleFactor, fy=videoScaleFactor)
	
	# Background subtraction
	foregroundMask = subtractor.apply(frame, None, -1)
	# opening removes false positives (white dots in background - the noise)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, kernel)
	# closing removes false negatives (black dots in actual object)
	subKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_CLOSE, subKernel)
	
	# threshold the frame - removes the random large changes
	ret, frameThresh = cv2.threshold(foregroundMask, 200, 255, cv2.THRESH_TOZERO)
	
	# Further noise reduction/dilation
	EKernel = np.ones((2, 2), np.uint8)
	DKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
	# erosion = cv2.erode(frameThresh, EKernel, iterations=1)  # gets rid of things
	# try and fill the gaps in objects
	dilation = cv2.dilate(frameThresh, DKernel, iterations=4)  # makes things more pronounced
	
	# This section displays the frames
	# show the two frames side by side (appears to be a video)
	cv2.imshow('Original frame', frame)
	cv2.moveWindow('Original frame', 0, 0)
	# get dimensions of the window (fix positioning of the other windows
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Original frame')
	
	cv2.imshow('Blob frame', foregroundMask)
	cv2.moveWindow('Blob frame', blobX + blobW, 0)
	
	cv2.imshow('Threshold', frameThresh)
	cv2.moveWindow('Threshold', 0, + blobY + blobH)
	
	cv2.imshow('Dilation & Erosion', dilation)
	cv2.moveWindow('Dilation & Erosion', blobX + blobW, + blobY + blobH)
	
	blurredDilation = cv2.GaussianBlur(dilation, (7, 7), 0)
	cv2.imshow('Blurred Dilation', blurredDilation)
	cv2.moveWindow('Blurred Dilation', blobX + (2 * blobW), 0)
	
	cv2.imshow('Contours', find_contours(blurredDilation))
	cv2.moveWindow('Contours', blobX + (2 * blobW), blobY + blobH)
	
	# was 15 before
	if cv2.waitKey(40) == 13:
		break

cap.release()
cv2.destroyAllWindows()
