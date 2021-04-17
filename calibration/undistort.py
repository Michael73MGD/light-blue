import cv2
import numpy as np
import sys


# You should replace these 3 lines with the output in calibration step
DIM=(640, 480)
K=np.array([[1501.5597250438875, 0.0, 320.77526075632784], [0.0, 1493.9696668107, 233.12519080752543], [0.0, 0.0, 1.0]])
D=np.array([[-5.41113709799924], [46.74932433849278], [-444.39018982174593], [2188.8422513635305]])
def undistort(img_path):
    img = cv2.imread(img_path)
    h,w = img.shape[:2]    
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)    
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    for p in sys.argv[1:]:
        undistort(p)