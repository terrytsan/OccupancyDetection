import logging
import cv2
import numpy as np
from BodyTracker import BodyTracker
from Body import Body

# constants
video = "Test10.mp4"
#video = "marbles5.mp4"
videoScaleFactor = 0.4
# videoScaleFactor = 1
# minimum area of contour before they are considered
minArea = 800
# Toggle writing output to file
writeToFile = True

# Create an object tracker object
bodTrack = BodyTracker()

# Number of people on the train
totalDown = 0
totalUp = 0

# Logging config. Disable with logging.CRITICAL
# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Create console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# End of logging config


# Return boolean, if line is crossed. True if line has been crossed. Requires y coord of line.
def line_crossed(body):
	# Skip check if there is no previous points (first frame body appears in)
	if len(body.visited) <= 1:
		return False
	
	# If the direction is down
	if body.direction == 0:
		# If the previous location_y is less than(<=) line_y AND current_y is greater than line_y
		if body.visited[-2][1] <= line_y < body.location[1]:
			# Line has been crossed
			logger.info(f"{body.ID} has crossed the line (down)")
			return True
	# If the direction is up
	if body.direction == 1:
		# If the previous location_y is greater(>=) than line_y AND current_y is less than line_y
		if body.visited[-2][1] >= line_y > body.location[1]:
			# Line has been crossed
			logger.info(f"{body.ID} has crossed the line (up)")
			return True
	return False


# Draws the contours, bounding box, and text on inputted image
def draw_graphics(contours, input_image):
	# Declare that we will use this variable is global
	global totalUp
	global totalDown
	# Draw the contours
	contour_color = (256, 0, 250)
	cv2.drawContours(input_image, contours, -1, contour_color, cv2.LINE_4)
	# holds all the rectangles (to be passed into the object tracker)
	rectangles = []
	rect_count = 0
	# Approximate a bounding rectangle around each contour
	for c in contours:
		x, y, w, h = cv2.boundingRect(c)
		rect_count = rect_count + 1
		# draw the rectangle on the passed in image
		cv2.rectangle(input_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		rectangles.append([x, y, x + w, y + h])
		# Print the area of the contour next to the rectangle
		cv2.putText(input_image, str(cv2.contourArea(c)), (x - 1, y - 1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
	# Get a list of tracked objects
	tracked_bodies = bodTrack.update(rectangles)
	
	# Draw the crossing line
	cv2.line(input_image, (0, line_y), (500, line_y), (0, 255, 0), 3)
	
	# Write text on the centroid
	for (ID, body) in tracked_bodies.items():
		body_x = body.location[0]
		body_y = body.location[1]
		# 0 is down
		if body.direction == 0:
			direction = "down"
		else:
			direction = "up"
		
		if line_crossed(body):
			cv2.putText(input_image, "line crossed", (100, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
			# If direction is down (leaving)
			if body.direction == 0:
				totalDown += 1
			# If direction is up (boarding)
			if body.direction == 1:
				totalUp += 1
		
		trackedObjectText = ("ID: %s %s" % (ID, direction))
		cv2.putText(input_image, (trackedObjectText), (body_x - 10, body_y - 10),
					cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
		# rectangle indicating centroid
		cv2.rectangle(input_image, (body_x, body_y - 1), (body_x + 1, body_y + 1), (0, 255, 0), 2)
	# Print out the number of rectangles in current frame
	cv2.putText(input_image, str(rect_count), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0))
	
	# Print out the number of people on board
	totalUpText = ("Up: %s" % (totalUp))
	totalDownText = ("Down: %s" % (totalDown))
	cv2.putText(input_image, totalUpText, (100, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
	cv2.putText(input_image, totalDownText, (200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0))
	
	
	return input_image


# Finds contours in given input image
def find_contours(input_image):
	# Declare this variable as global
	global minArea
	# Array to hold contours meeting minimum area
	reduced_contours = []
	# Find contours (only outermost ones)
	contours, hierarchy = cv2.findContours(input_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# Go through each contour keeping ones that meet minArea
	for c in contours:
		if cv2.contourArea(c) > minArea:
			reduced_contours.append(c)
	return reduced_contours


# Perform background subtraction on input frame
def subtract_background(input_frame, subtractor_function):
	# get dimensions of the window (fix positioning of the other windows)
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Original frame')
	
	# Background subtraction
	foregroundMask = subtractor_function.apply(input_frame, None, -1)
	
	# opening removes false positives (white dots in background - the noise)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, kernel)
	# closing removes false negatives (black dots in actual object)
	subKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
	# foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_CLOSE, subKernel)
	
	# threshold the frame - removes the random large changes
	ret, frameThresh = cv2.threshold(foregroundMask, 200, 255, cv2.THRESH_TOZERO)
	
	# Further noise reduction/dilation
	EKernel = np.ones((2, 2), np.uint8)
	DKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
	# erosion = cv2.erode(frameThresh, EKernel, iterations=1)  # gets rid of things
	# try and fill the gaps in objects
	dilation = cv2.dilate(frameThresh, DKernel, iterations=4)  # makes things more pronounced
	
	# Show the intermediate steps as windows
	cv2.imshow('Blob frame', foregroundMask)
	cv2.moveWindow('Blob frame', blobX + blobW, 0)
	
	cv2.imshow('Threshold', frameThresh)
	cv2.moveWindow('Threshold', 0, + blobY + blobH)
	
	cv2.imshow('Dilation & Erosion', dilation)
	cv2.moveWindow('Dilation & Erosion', blobX + blobW, + blobY + blobH)
	
	return dilation


# Load the video
cap = cv2.VideoCapture(video)
# cv.Flip(frame, flipMode=-1)

# want to detect shadows so they can be thresholded
subtractor = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=20, detectShadows=1)
subtractorTwo = cv2.createBackgroundSubtractorKNN()
subtractor.setShadowThreshold(0.7)
logger.debug(f"Shadow threshold: {subtractor.getShadowThreshold()}")
subtractor.setBackgroundRatio(0.5)
logger.debug(f"Background ratio: {subtractor.getBackgroundRatio()}")

frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
writer = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (int(frame_w * videoScaleFactor), int(frame_h * videoScaleFactor)))
# Set the line to be half way
line_y = int((frame_h * videoScaleFactor * 0.5))

# Play the video
while 1:
	ret, frame = cap.read()
	if not ret:
		break
	
	# resize frame
	frame = cv2.resize(frame, (0, 0), fx=videoScaleFactor, fy=videoScaleFactor)
	# frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred_frame = cv2.GaussianBlur(frame, (7, 7), 0)
	# Perform background subtraction
	subtracted_frame = subtract_background(blurred_frame, subtractor)
	# This section displays the frames
	# show the two frames side by side (appears to be a video)
	cv2.imshow('Original frame', frame)
	cv2.moveWindow('Original frame', 0, 0)
	# get dimensions of the window (fix positioning of the other windows
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Original frame')
	
	blurredDilation = cv2.GaussianBlur(subtracted_frame, (7, 7), 0)
	cv2.imshow('Blurred Dilation', blurredDilation)
	cv2.moveWindow('Blurred Dilation', blobX + (2 * blobW), 0)
	
	# Get the contours in the image
	found_contours = find_contours(blurredDilation)
	
	blank_image = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)
	cv2.imshow('Contours', draw_graphics(found_contours, frame))
	cv2.moveWindow('Contours', blobX + (2 * blobW), blobY + blobH)
	
	if writeToFile:
		writer.write(draw_graphics(found_contours, frame).astype('uint8'))
	
	# was 15 before
	if cv2.waitKey(40) == 13:
		break

cap.release()
cv2.destroyAllWindows()
