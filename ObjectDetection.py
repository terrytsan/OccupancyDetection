import cv2
import numpy as np

# constants
video = "nt3D26lrkho.mp4"
videoScaleFactor = 0.5

# Load the video
cap = cv2.VideoCapture(video)

# subtractor for background subtractor
subtractor = cv2.createBackgroundSubtractorMOG2()

# Play the video
while cap.isOpened():
	ret, frame = cap.read()
	# resize frame
	frame = cv2.resize(frame, (0, 0), fx=videoScaleFactor, fy=videoScaleFactor)
	
	# Kernel for the background subtractor
	subKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
	foregroundMask = subtractor.apply(frame)
	# opening removes false positives (white dots in background)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, subKernel)
	# closing removes false negatives (black dots in actual object)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_CLOSE, subKernel)
	
	# erode the frame, removes noise
	EKernel = np.ones((3, 3), np.uint8)
	erosion = cv2.erode(foregroundMask, EKernel, iterations=2)
	dilation = cv2.dilate(erosion, EKernel, iterations=1)
	
	# threshold the frame - removes the random large changes
	ret, frameThresh = cv2.threshold(dilation, 200, 255, cv2.THRESH_TOZERO)
	
	# This section displays the frames
	# show the two frames side by side (appears to be a video)
	cv2.imshow('Original frame', frame)
	cv2.moveWindow('Original frame', 0, 0)
	# get dimensions of the window (fix positinoing of the other windows
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Original frame')
	
	cv2.imshow('Blob frame', foregroundMask)
	cv2.moveWindow('Blob frame', blobX + blobW, blobY)
	
	cv2.imshow('Threshold (best)', frameThresh)
	cv2.moveWindow('Threshold (best)', blobX, + blobY + blobH)
	
	if cv2.waitKey(15) == 13:
		break

cap.release()
cv2.destroyAllWindows()
