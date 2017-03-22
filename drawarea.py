# coding:utf-8
import sys

import importlib
importlib.reload(sys)

import cv2
import time
import imutils

# 当鼠标按下时设置 要进行绘画
drawing = False

# 如果mode为True时就画矩形，按下‘m'变为绘制曲线
GetArea = True

globalx, globaly = -1,-1

# 创建回调函数，用于设置滚动条的位置
def drawcircle(event,x,y,flags,param):
	global globalx,globaly,drawing,GetArea,img,order
	
	if not GetArea:
		return
	# 当按下左键时，返回起始的位置坐标
	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
		globalx,globaly = x,y
	# 当鼠标左键按下并移动则是绘画圆形，event可以查看移动，flag查看是否按下
	elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
		img = order.copy()
		cv2.rectangle(img,(globalx,globaly),(x,y),(0, 255, 0),2)
	
	if event == cv2.EVENT_LBUTTONUP:
		if drawing == True:
			img = order.copy()
			cv2.rectangle(img,(globalx,globaly),(x,y),(0, 255, 0),2)
			drawing = False
			print((globalx,globaly,x,y))	

camera = cv2.VideoCapture(0)
time.sleep(0.25)
(grabbed, image) = camera.read()
image = imutils.resize(image, width=min(400, image.shape[1]))
order = image.copy()
img = image.copy()

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.setMouseCallback('image',drawcircle)

while True:
	cv2.imshow('image',img)

	key = cv2.waitKey(10)
	if key == ord('o'):
		GetArea = False
	if key == ord("q"):
		break
		
camera.release()		
cv2.destroyAllWindows()