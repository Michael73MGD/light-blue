import cv2 as cv
import numpy as np
import socket
import sys 
import urllib

def take_picture():
    img_url = "http://192.168.1.34:8000/stream.mjpg"

    stream = urllib.request.urlopen(img_url)
    bytes = b''
    while True:
        bytes += stream.read(1024)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            frame = cv.imdecode(np.fromstring(jpg, dtype=np.uint8), cv.IMREAD_COLOR)
            frame = undistort(frame)
            cv.imwrite("cv_test/frame.jpg", frame)
            return frame


def undistort(img):
    DIM=(640, 480)
    K=np.array([[1501.5597250438875, 0.0, 320.77526075632784], [0.0, 1493.9696668107, 233.12519080752543], [0.0, 0.0, 1.0]])
    D=np.array([[-5.41113709799924], [46.74932433849278], [-444.39018982174593], [2188.8422513635305]])
    h,w = img.shape[:2]    
    map1, map2 = cv.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv.CV_16SC2)
    undistorted_img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)    
    return undistorted_img