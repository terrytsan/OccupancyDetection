import cv2
import numpy as np

#constants
video = "nt3D26lrkho.mp4"
videoScaleFactor = 0.5

# Load the video
cap = cv2.VideoCapture(video)

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

subtractor = cv2.createBackgroundSubtractorMOG2()

# This kernel will be used to remove noise
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# Counter for frames. Outputs the current frame number
count = 0
# Play the video
while (1):
	ret, frame = cap.read()
	# resize frame
	frame = cv2.resize(frame, (0, 0), fx=videoScaleFactor, fy=videoScaleFactor)
	# apply guassian blur
	#frame = cv2.GaussianBlur(frame, (5, 5), 0)
	
	foregroundMask = subtractor.apply(frame)
	#opening removes false positives (white dots in background)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, kernel)
	#closing removes false negatives (black dots in actual object)
	foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_CLOSE, kernel)
	
	# erode the frame, removes noise
	EKernel = np.ones((6,6), np.uint8)
	erosion = cv2.erode(foregroundMask, EKernel, iterations=2)
	
	dilation = cv2.dilate(erosion, EKernel, iterations=1)
	
	
	# threshold the frame
	# frameThresh = cv2.adaptiveThreshold(foregroundMask, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
	ret, frameThresh = cv2.threshold(dilation, 200, 255, cv2.THRESH_TOZERO)
	
	# find countours
	
	
	# This section displays the frames
	
	# show the two frames side by side (appears to be a video)
	cv2.imshow('Blob frame', foregroundMask)
	# get dimensions of window
	blobX, blobY, blobW, blobH = cv2.getWindowImageRect('Blob frame')
	cv2.moveWindow('Blob frame', 0, 0)
	
	# show the original frame
	cv2.imshow('Original frame', frame)
	cv2.moveWindow('Original frame', blobX + blobW, blobY)
	
	# show the keypoints
	cv2.imshow('Threshold', frameThresh)
	cv2.moveWindow('Threshold', blobX, + blobY + blobH)
	
	if cv2.waitKey(15) == 13:
		break

cap.release()
cv2.destroyAllWindows()
