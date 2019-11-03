# Occupancy Detection

This is a project with the aim to count objects crossing a fixed point using a camera. 

## Getting Started

Use `video` from `ObjectDetection` to change the input video feed. Use 0 for webcam feed.  
Adjust `videoScaleFactor` to adjust the size of the frame.  
Adjust `minArea` to set the minimum size of an object for it to be tracked.  

### Prerequisites

* Python 3.7
* OpenCV 2
* Numpy


### Features

* Identify moving objects in the frame.
* Counts the number objects moving up/down the frame.
* Shows size of objects moving in frame.
