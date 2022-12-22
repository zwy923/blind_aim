import time
import cv2
import numpy as np
from PIL import ImageGrab
import yolov5
import pyautogui
import win32api
import win32con

#移动鼠标位置
def move_mouse(x,y):
    pyautogui.moveTo(x,y)
# Load the YOLOv5 model
model = yolov5.load('yolov5s.pt')
aim_mouse = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
while True:
    # Capture the screen using OpenCV
    screen = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_BGR2RGB)
    # Run object detection on the screen
    predictions = model(screen)
    df=predictions.pandas().xyxy[0].sort_values('confidence',ascending=False)
    # Display the result
    try:
        data=df[df['name'] == 'person'].iloc[0].to_dict()
    except IndexError:
        print("no target")
        time.sleep(1)
    else:
        aim_mouse = win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
        x=(data['xmin']+data['xmax'])/2
        y=(data['ymin']+data['ymax'])/2
        print(x,y)
        if(aim_mouse):
            move_mouse(x,y)