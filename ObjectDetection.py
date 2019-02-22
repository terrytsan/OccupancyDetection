import cv2
import numpy as np

# constants
video = "example_01.mp4"
videoScaleFactor = 1
# minimum size of rectangles before they are shown
minRecSize = 3000


# Draws a bounding box around each contour (of a minimum area) and show on the input image
def draw_box(contours, image):
	for c in contours:
		x, y, w, h = cv2.boundingRect(c)
		# Only draw rectangles larger than minimumRecSize
		if (w*h) > minRecSize:
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)


# Finds contours in given input image
def find_contours(inputimage):
	threshold = 100
	# Detect edges using Canny
	# Used to detect the jagged edges of the image
	canny_output = cv2.Canny(inputimage, threshold, threshold * 2)
	# Find contours
	contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# Draw contours
	drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
	color = (256, 0, 250)
	# cv2.drawContours(drawing, contours, i, color, cv2.FILLED, cv2.LINE_8, hierarchy, 0)
	cv2.drawContours(drawing, contours, -1, color, cv2.LINE_4)
	# Draw bounding rectangles
	draw_box(contours, drawing)
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
	dilation = cv2.dilate(frameThresh, DKernel, iterations=5)  # makes things more pronounced
	
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
