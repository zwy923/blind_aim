import time
import cv2
import numpy as np
from PIL import ImageGrab
import torch
import yolov5
import pyautogui
import win32api
import win32con
from pid import PID

# Load the YOLOv5 model
model = yolov5.load('yolov5s.pt')

y_correction_factor = 10  # 截图位置修正， 值越大截图窗口向上

screen_x, screen_y = 2560,1440
window_x,window_y= 350,350

pid = PID(0.005,30,-30,0.4,0.08,0)

screen_x_center = screen_x / 2
screen_y_center = screen_y / 2
edge_x = screen_x_center - window_x / 2
edge_y = screen_y_center - window_y / 2


grab_window= (
    int(screen_x / 2 - window_x / 2),
    int(screen_y / 2 - window_y / 2 - 10),
    int(screen_x / 2 + window_x / 2),
    int(screen_y / 2 + window_y / 2 - 10))


aim_x = 200  # aim width
aim_x_left = int(screen_x_center - aim_x / 2)  # 自瞄左右侧边距
aim_x_right = int(screen_x_center + aim_x / 2)

aim_y = 400  # aim width
aim_y_up = int(screen_y_center - aim_y / 2 - y_correction_factor)  # 自瞄上下侧边距
aim_y_down = int(screen_y_center + aim_y / 2 - y_correction_factor)


#移动鼠标位置
def move_mouse(x,y):
    pyautogui.moveTo(x,y)

def xyxy2xywh(xyxy):

    if len(xyxy.shape) == 2:
        w, h = xyxy[:, 2] - xyxy[:, 0] + 1, xyxy[:, 3] - xyxy[:, 1] + 1
        xywh = np.concatenate((xyxy[:, 0:2], w[:, None], h[:, None]), axis=1)
        return xywh.astype("int")
    elif len(xyxy.shape) == 1:
        (left, top, right, bottom) = xyxy
        width = right - left + 1
        height = bottom - top + 1
        return np.array([left, top, width, height]).astype('int')
    else:
        raise ValueError("Input shape not compatible.")


@torch.no_grad()
def aim():
    while True:
        # Capture the screen using OpenCV
        screen = cv2.cvtColor(np.array(ImageGrab.grab(grab_window)), cv2.COLOR_BGR2RGB)
        # Run object detection on the screen
        predictions = model(screen)
        df=predictions.pandas().xyxy[0].sort_values('confidence',ascending=False)
        # Display the result
        try:
            data=df[df['name'] == 'person'].iloc[0].to_dict()
            xmin=data['xmin']
            ymin=data['ymin']
            xmax=data['xmax']
            ymax=data['ymax']
            xyxy=np.array([xmin+screen_x/2-window_x/2,ymin+screen_y/2-window_y/2,xmax+screen_x/2-window_x/2,ymax+screen_y/2-window_y/2])
            target_xywh = xyxy2xywh(xyxy)
            target_xywh_x = target_xywh[0]
            target_xywh_y = target_xywh[1]
        except IndexError:
            print("no target")
            time.sleep(1)
        else:
            final_x = target_xywh_x
            final_y = target_xywh_y - 0.15 * target_xywh[3]
            if aim_x_left < target_xywh_x < aim_x_right and aim_y_up < target_xywh_y < aim_y_down:
                pid_x = int(pid.calculate(final_x, 0))
                pid_y = int(pid.calculate(final_y, 0))
                aim_mouse = win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
                if(aim_mouse):
                    move_mouse(final_x+pid_x,final_y+pid_y)
        #停止自瞄
        stop_mouse = win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
        if(stop_mouse):
            print("stop")
            break

aim()
