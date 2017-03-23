# coding=gbk
# �����Ҫ�������
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

# ������������������������
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# ���video����ΪNone����ô���Ǵ�����ͷ��ȡ����
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
 
# �������Ƕ�ȡһ����Ƶ�ļ�
else:
	camera = cv2.VideoCapture(args["video"])
 
# ��ʼ����Ƶ���ı���֡
firstFrame = None

# ��ʼ����Ƶ������һ֡
lastFrame = None
framecount = 0
# ������Ƶ��ÿһ֡
while True:
	# ��ȡ��ǰ֡����ʼ��occupied/unoccupied�ı�
	(grabbed, frame) = camera.read()
	text = "Unoccupied"
 
	# �������ץȡ��һ֡��˵�����ǵ�����Ƶ�Ľ�β
	if not grabbed:
		break
 
	# ������֡�Ĵ�С��ת��Ϊ�ҽ�ͼ���Ҷ�����и�˹ģ��
	frame = imutils.resize(frame, width=500)
	framedetect = frame.copy()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	height, width = frame.shape[:2]
 
	# �����һ֡��None��������г�ʼ��
	if firstFrame is None:
		firstFrame = gray
		continue
		
	if lastFrame is None:
		lastFrame = gray
		continue
		
	# ���㵱ǰ֡�͵�һ֡�Ĳ�ͬ
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# ��չ��ֵͼ�����׶���Ȼ���ҵ���ֵͼ���ϵ�����
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_,cnts,hierarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	if framecount == 0:
		# ���㵱ǰ֡����һ֡�Ĳ�ͬ
		frameDeltalast = cv2.absdiff(lastFrame, gray)
		threshlast = cv2.threshold(frameDeltalast, 25, 255, cv2.THRESH_BINARY)[1]
 
		# ��չ��ֵͼ�����׶���Ȼ���ҵ���ֵͼ���ϵ�����
		threshlast = cv2.dilate(threshlast, None, iterations=2)
		(_,cntslast,hierarchylast) = cv2.findContours(threshlast.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		lastFrame = gray
	
	movecounter = 0

	for d in cntslast:
		movecounter = movecounter + 1
			
	# ��������
	detectcnts = detect(framedetect)
	
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
		
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		# ���������ı߽���ڵ�ǰ֡�л����ÿ�
		
		(x, y, w, h) = cv2.boundingRect(c)
		
		# ȥ������ͼ��ı߿�
		if x == 0 or y == 0:
			continue

		if x + w >= width or y + h >= height:
			continue
			
		for (xA, yA, xB, yB) in detectcnts:
			if isSame(x, y, x + w, y + h, xA, yA, xB, yB,):
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
				text = "Occupied"
	
	
	# draw the text and timestamp on the frame
	# �ڵ�ǰ֡��д�����Լ�ʱ���
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
 
 
	#��ʾ��ǰ֡����¼�û��Ƿ��°���
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", threshlast)
	cv2.imshow("Frame Delta", frameDeltalast)
	key = cv2.waitKey(1)
	
	# ���q�������£�����ѭ��
	if key == ord("q"):
		break
 
	framecount =  framecount + 1
	if framecount == 9:
		framecount = 0
# �����������Դ���رմ򿪵Ĵ���
camera.release()
cv2.destroyAllWindows()