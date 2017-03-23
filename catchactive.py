# coding=gbk
# 导入必要的软件包
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2


samepercent = 0.4

def detect(image):
	'''
	orig = image.copy()
	'''
	# detect people in the image
	(rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
		padding=(8, 8), scale=1.05)
	'''
	# draw the original bounding boxes
	for (x, y, w, h) in rects:
		cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)
	'''
	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
	return pick

def inSamePercent(Ax1, Ax2, Bx1, Bx2):
	if Ax1 - ((Ax2 - Ax1)*samepercent) < Bx1 and Ax1 + ((Ax2 - Ax1)*samepercent) > Bx1:
		if Ax2 - ((Ax2 - Ax1)*samepercent) < Bx2 and Ax2 + ((Ax2 - Ax1)*samepercent) > Bx2:
			return True
	
	return False
	
def isSame(xA1,yA1,xA2,yA2,xB1,yB1,xB2,yB2):
	if inSamePercent(xA1, xA2, xB1, xB2) and inSamePercent(yA1, yA2, yB1, yB2):
		return True
	else:
		return False

nomovecount = 0

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# 创建参数解析器并解析参数
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# 如果video参数为None，那么我们从摄像头读取数据
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
 
# 否则我们读取一个视频文件
else:
	camera = cv2.VideoCapture(args["video"])
 
# 初始化视频流的背景帧
firstFrame = None

# 初始化视频流的上一帧
lastFrame = None
framecount = 0
# 遍历视频的每一帧
while True:
	# 获取当前帧并初始化occupied/unoccupied文本
	(grabbed, frame) = camera.read()
	text = "Unoccupied"
 
	# 如果不能抓取到一帧，说明我们到了视频的结尾
	if not grabbed:
		break
 
	# 调整该帧的大小，转换为灰阶图像并且对其进行高斯模糊
	frame = imutils.resize(frame, width=500)
	framedetect = frame.copy()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	height, width = frame.shape[:2]
 
	# 如果第一帧是None，对其进行初始化
	if firstFrame is None:
		firstFrame = gray
		continue
		
	if lastFrame is None:
		lastFrame = gray
		continue
		
	# 计算当前帧和第一帧的不同
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_,cnts,hierarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	if framecount == 0:
		# 计算当前帧和上一帧的不同
		frameDeltalast = cv2.absdiff(lastFrame, gray)
		threshlast = cv2.threshold(frameDeltalast, 25, 255, cv2.THRESH_BINARY)[1]
 
		# 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
		threshlast = cv2.dilate(threshlast, None, iterations=2)
		(_,cntslast,hierarchylast) = cv2.findContours(threshlast.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		lastFrame = gray
	
	movecounter = 0

	for d in cntslast:
		movecounter = movecounter + 1
			
	# 遍历轮廓
	detectcnts = detect(framedetect)
	
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
		
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		# 计算轮廓的边界框，在当前帧中画出该框
		
		(x, y, w, h) = cv2.boundingRect(c)
		
		# 去除紧贴图像的边框
		if x == 0 or y == 0:
			continue

		if x + w >= width or y + h >= height:
			continue
			
		for (xA, yA, xB, yB) in detectcnts:
			if isSame(x, y, x + w, y + h, xA, yA, xB, yB,):
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
				text = "Occupied"
	
	
	# draw the text and timestamp on the frame
	# 在当前帧上写文字以及时间戳
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	if movecounter == 0:
		nomovecount = nomovecount + 1
		if nomovecount == 3600:
			firstFrame = gray
			nomovecount = 0
	else :
		nomovecount = 0
		
	cv2.putText(frame, "movecount = "+str(movecounter), (10, 50),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, "nomovecount = "+str(nomovecount), (10, 100),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
 
	#显示当前帧并记录用户是否按下按键
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", threshlast)
	cv2.imshow("Frame Delta", frameDeltalast)
	key = cv2.waitKey(1)
	
	# 如果q键被按下，跳出循环
	if key == ord("q"):
		break
 
	framecount =  framecount + 1
	if framecount == 9:
		framecount = 0
# 清理摄像机资源并关闭打开的窗口
camera.release()
cv2.destroyAllWindows()