# coding=gbk

# import the necessary packages
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import time

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
camera = cv2.VideoCapture(0)
time.sleep(0.25)

# loop over the image paths
# 遍历视频的每一帧
while True:
	# 获取当前帧并初始化occupied/unoccupied文本
	(grabbed, image) = camera.read()
	text = "Unoccupied"
 
	# 如果不能抓取到一帧，说明我们到了视频的结尾
	if not grabbed:
		break
 
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy
	#image = cv2.imread(imagePath)
	image = imutils.resize(image, width=min(400, image.shape[1]))
	orig = image.copy()

	# detect people in the image
	(rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
		padding=(8, 8), scale=1.05)

	# draw the original bounding boxes
	for (x, y, w, h) in rects:
		cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

	# draw the final bounding boxes
	for (xA, yA, xB, yB) in pick:
		cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

	# show the output images
	#cv2.imshow("Before NMS", orig)
	cv2.imshow("After NMS", image)
	key = cv2.waitKey(1)
	
	# 如果q键被按下，跳出循环
	if key == ord("q"):
		break
		
# 清理摄像机资源并关闭打开的窗口
camera.release()
cv2.destroyAllWindows()