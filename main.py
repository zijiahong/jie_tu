import win32gui
from PIL import ImageGrab
import time
import os.path
import sys
hand1 = win32gui.FindWindow(None,"地下城与勇士")
name = "images1/"
# current_scene =  ImageGrab.grab(win32gui.GetWindowRect(hand1))
# name = name + str(int(time.time()))
# name  = name  + ".png"
# current_scene.save(name)

while True :
    time.sleep(2)
    name = "images/"
    current_scene =  ImageGrab.grab(win32gui.GetWindowRect(hand1))
    name = name + str(int(time.time()))
    name  = name  + ".jpg"
    current_scene.save(name)



