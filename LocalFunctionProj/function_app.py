import logging
import azure.functions as func
from collections import deque
from io import BytesIO
import numpy as np
import cv2
import imutils
import time
from PIL import Image

app = func.FunctionApp()

@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob", 
				  path="PATH/TO/BLOB",
				  connection="CONNECTION_SETTING")
@app.blob_output(arg_name="outputblob",
				path="newblob/test.txt",
				connection="<BLOB_CONNECTION_SETTING>")
def main(myblob: func.InputStream, outputblob: func.Out[str]):
	# define the lower and upper boundaries of the "green ball in the HSV color space,
	#  then initialize the list of tracked points
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	pts = deque(maxlen=64)
	vs = cv2.VideoCapture(myblob)
	# allow the camera or video file to warm up
	time.sleep(2.0)

	frameList = []

	# keep looping
	while True:
		# grab the current frame
		frame = vs.read()
		# handle the frame from VideoCapture or VideoStream
		frame = frame[1]
		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
		if frame is None:
			break
		# resize the frame, blur it, and convert it to the HSV color space
		frame = imutils.resize(frame, width=400)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
		# construct a mask for the color "green", then perform a series of dilations 
		# and erosions to remove any small blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
	
		# find contours in the mask and initialize the current (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		center = None
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame, then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
		# update the points queue
		pts.appendleft(center)
	
		# loop over the set of tracked points
		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore them
			if pts[i - 1] is None or pts[i] is None:
				continue
			# otherwise, compute the thickness of the line and draw the connecting lines
			thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
		# show the frame to our screen
		cv2.imshow("Frame", frame)
		frameList.append(frame)
		key = cv2.waitKey(1) & 0xFF
	
	vs.release()
	# close all windows
	cv2.destroyAllWindows()

	images = [Image.fromarray(cv2.cvtColor(frames,cv2.COLOR_BGR2RGB)) for frames in frameList]
	#images[0].save('./pillow_imagedraw.gif',
	#			save_all=True, append_images=images[1:], optimize=True, quality=50, duration=40, loop=0)


	#save to stream
	gifStream = BytesIO()
	images[0].save(gifStream,
               save_all=True, append_images=images[1:], optimize=False, duration=40, loop=0)

	gifStream.seek(0)

	outputblob.set(gifStream)
	logging.info(f"Python blob trigger function processed blob \n"
				f"Name: {myblob.name}\n"
				f"Blob Size: {myblob.length} bytes")
	return "ok"