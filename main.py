import time
import cv2
import numpy as np
from PIL import ImageGrab
import torch
import yolov5
import pyautogui
import win32api
import win32con
import serial
from pid import PID

# Load the YOLOv5 model
model = yolov5.load('yolov5s.pt')

y_correction_factor = 10  # 截图位置修正， 值越大截图窗口向上

screen_x, screen_y = 2560,1440
window_x,window_y= 650,650
y_portion = 0.2
pid = PID(0.005,30,-30,0.4,0.08,0)


grab_window= (
    int(screen_x / 2 - window_x / 2),
    int(screen_y / 2 - window_y / 2),
    int(screen_x / 2 + window_x / 2),
    int(screen_y / 2 + window_y / 2))


#移动鼠标位置
def move_mouse(x,y):
    pyautogui.moveTo(x,y)


@torch.no_grad()
def aim():
    aim_mouse = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
    while True:
        # Capture the screen using OpenCV
        screen = cv2.cvtColor(np.array(ImageGrab.grab(grab_window)), cv2.COLOR_BGR2RGB)
        # Run object detection on the screen
        predictions = model(screen)
        x, y = pyautogui.position()

        df=predictions.pandas().xyxy[0].sort_values('confidence',ascending=False)
        # Display the result
        try:
            data=df[df['name'] == 'person'].iloc[0].to_dict()
        except IndexError:
            print("no target")
        else:
            aim_mouse = win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
            x=(data['xmin']+data['xmax'])/2+screen_x / 2 - window_x / 2
            y=(data['ymin']+data['ymax'])/2+screen_y / 2 - window_y / 2 - 20
            print(x,y)
            if(aim_mouse):
                move_mouse(x,y)

        #停止自瞄
        stop_mouse = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
        if(stop_mouse):
            print("stop")
            break

aim()
