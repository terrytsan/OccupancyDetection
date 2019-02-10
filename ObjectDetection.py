import cv2
import numpy as np

# Load the video
cap = cv2.VideoCapture("nt3D26lrkho.mp4")

# # play the video
# while cap.isOpened():
# 	ret, frame = cap.read()
# 	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# 	cv2.imshow('Video frame', gray)
#
# 	if cv2.waitKey(1) == 13:
# 		break;
#
# cap.release()
# cv2.destroyAllWindows()

# subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
subtractor = cv2.createBackgroundSubtractorMOG2()

# This kernel will be used to remove noise
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

# Counter for frames. Outputs the current frame number
count = 0
# Play the video
while (1):
	ret, frame = cap.read()
	# resize frame
	frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
	foregroundMask = subtractor.apply(frame)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, kernel)
	
	# show the two frames side by side (appears to be a video)
	cv2.imshow('Blob frame', foregroundMask)
	# get dimensions of window
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Blob frame')
	cv2.moveWindow('Blob frame', 0, 0)
	cv2.imshow('Original frame', frame)
	cv2.moveWindow('Original frame', blobX + blobW, blobY)
	
	# Testing detecting key points
	
	# Setting the parameters for blob detection
	blobParams = cv2.SimpleBlobDetector_Params()
	
	# blobParams.minThreshold = 0
	# blobParams.maxThreshold = 256
	blobParams.filterByColor = 1
	blobParams.blobColor = 255
	
	detector = cv2.SimpleBlobDetector_create(blobParams)
	keypoints = detector.detect(foregroundMask)
	# problem with drawKeypoints in this version of openCV
	frameWithKeyPoints = cv2.drawKeypoints(foregroundMask, keypoints, outImage=np.array([]), color=(0, 0, 255),
										   flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	
	# show the keypoints
	cv2.imshow('Keypoints', frameWithKeyPoints)
	cv2.moveWindow('Keypoints', blobX, + blobY + blobH)
	
	# print the number of the current frame
	count = count + 1
	print(count)
	
	if cv2.waitKey(15) == 13:
		break

cap.release()
cv2.destroyAllWindows()
