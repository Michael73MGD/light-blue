import cv2 as cv
import numpy as np
import sys 
import urllib.request

def take_picture():
    img_url = "http://192.168.1.34:8000/stream.mjpg"

    stream = urllib.request.urlopen(img_url)
    bytes = b''
    while True:
        bytes += stream.read(1024)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            print("snap!")
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            frame = cv.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_COLOR)
            #frame = undistort(frame)
            #cv.imwrite("cv_test/frame.jpg", frame)
            return frame


def undistort(img):
    DIM=(640, 480)
    K=np.array([[1501.5597250438875, 0.0, 320.77526075632784], [0.0, 1493.9696668107, 233.12519080752543], [0.0, 0.0, 1.0]])
    D=np.array([[-5.41113709799924], [46.74932433849278], [-444.39018982174593], [2188.8422513635305]])
    h,w = img.shape[:2]    
    map1, map2 = cv.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv.CV_16SC2)
    undistorted_img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)    
    return undistorted_img

def extract_HSV_channels(img):
    H = img[:, :, 0]
    S = img[:, :, 1]
    V = img[:, :, 2]

    cv.imwrite('cv_test/H.jpg', H)
    cv.imwrite('cv_test/S.jpg', S)
    cv.imwrite('cv_test/V.jpg', V)

def draw_grid(img, x_offset, y_offset, square_size):
    for i in range(5):
        x = x_offset+square_size*i
        x_p = x+5
        y = y_offset+square_size*i
        y_p = y+5
        img[x:x_p,:,:] = (255,0,0)
        img[:,y:y_p,:] = (255,0,0)
    
    return img

def crop_quadrant(img, x_offset, y_offset, square_size):
    x1 = x_offset
    x2 = x_offset+4*square_size

    y1 = y_offset
    y2 = y_offset+4*square_size

    img[:x1, :, :] = (0,0,0)
    img[x2:, :, :] = (0,0,0)
    img[:, :y1, :] = (0,0,0)
    img[:, y2:, :] = (0,0,0)
    return img


def get_contours(img, c_range):
    min_size = 400

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    extract_HSV_channels(hsv)
    mask = cv.inRange(hsv, c_range[0], c_range[1])
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for i, c in enumerate(contours):
        if(cv.contourArea(c) < min_size):
            del contours[i]
    
    return contours

def get_centroid(contour):
    M = cv.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return (cx, cy)



    

x_o = 17
y_o = 67
s_s = 110

S_mask = [(0, 50, 0), (255, 255, 255)]
light_blue = [(105, 130, 130), (115, 190, 190)]
red = [(175, 125, 80), (185, 160, 120)]
dark_blue = [(110, 140, 75), (120, 195, 125)]
orange = [(0, 125, 125), (5, 180, 180)]
yellow = [(15, 130, 120), (30, 170, 195)]
green = [(83, 60, 90), (100, 115, 150)]



img = cv.imread("Q1.jpg")
#hsv = cv.cvtColor(crop_quadrant(img, x_o, y_o, s_s), cv.COLOR_BGR2HSV)
#mask = cv.inRange(hsv, green[0], green[1])
#img = cv.bitwise_and(hsv, hsv, mask=mask)
img = draw_grid(img, x_o, y_o, s_s)
#img = crop_quadrant(img, x_o, y_o, s_s)
#extract_HSV_channels(img)
cv.imwrite("grid2.jpg", img)