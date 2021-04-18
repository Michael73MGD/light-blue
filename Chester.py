#You must run this with: sudo -E python3 Chester.py
from stockfish import Stockfish         #Check AI.py for info on this \/
stockfish = Stockfish("/home/jack/projects/light-blue/stockfish_20090216_x64",parameters={"Threads": 2})
import serial   #Confusingly, the package for this is pySerial not serial
import time
import sys
import paramiko
import random_FEN
import urllib
from cv_cmds import take_picture, crop_quadrant, get_centroid, get_contours, extract_HSV_channels
import cv2 as cv
import numpy as np
import signal
import math

class Chester:
    x = 0
    y = 0
    z = 15
    ser = None
    grab_height = 0
    move_height = 20
    vision_height = 80
    normal_speed = 2750 #typical feedrate for moving
    z_speed = 4000 #feedrate for movement
    z_vel = 80/17 # constant for figuring out how long to wait in the z direction
    xy_vel = 150/4.75
    ssh = None

    quadrant_params = {
        "x_offset": [17, 25, 20, 13],
        "y_offset": [67, 65, 140, 135],
        "square_size": [110, 110, 115, 110],
        "square_offset": [(0, 4), (4, 4), (4, 0), (0, 0)] #letter, number
    }

    quadrant_pos = [(60, 15), (160, 15), (160, 100), (60, 100)]

    letterDictionary = {
            "a":8,
            "b":7,
            "c":6,
            "d":5,
            "e":4,
            "f":3,
            "g":2,
            "h":1,
        }

    piece_color_dict = {
        'king':[(75, 60, 50), (100, 160, 150)],
        'queen':[(105, 130, 130), (115, 190, 190)],
        'bishop':[(170, 70, 20), (185, 170, 120)],
        'knight':[(15, 90, 120), (30, 170, 195)],
        'rook':[(105, 70, 20), (120, 195, 125)],
        'pawn':[(0, 130, 80), (5, 180, 210)]
    }

    x_offset = 20
    y_offset = 0
    square_size = 25.4

    def __init__(self, serial):
        self.ser = serial

        self.ser.write(b'G92 Z0\r\n')     #Tell the printer that its current Z position is 0
        time.sleep(1)
        self.move_to_z(self.move_height)
        time.sleep(1)
        self.ser.write(b'G28 X0 Y0\r\n')  #Home the X and Y axis because their position is unknown 
        time.sleep(1)

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect("raspberrypi", username="pi", password="chester")

    @staticmethod
    def check_legal_move(fen_state, move):
        stockfish.set_fen_position(fen_state)
        stockfish._put("go perft 1")
        while True:
            l = stockfish._read_line()
            if(l[0:4] == "Node"):
                return False
            else:
                if(move[0:2] == l[0:2] and move[2:4] == l[2:4]):
                    return True

    def move_to_z(self, pos):
        self.ser.write(bytes(f'G1 Z{pos} F{self.z_speed}\r\n', 'utf-8'))     #Move the Z axis up and out of the way of the pieces
        dist = abs(self.z-pos)
        time.sleep(dist/self.z_vel)
        self.z = pos
        self.ser.write(bytes(f'G1 F{self.normal_speed}\r\n', 'utf-8'))  
        time.sleep(1)

    def move_to_xy(self, xpos, ypos):
        self.ser.write(bytes(f'G1 X{xpos} Y{ypos} F{self.normal_speed}\r\n', 'utf-8'))
        dist = max(abs(self.x-xpos), abs(self.y-ypos))
        time.sleep(dist/self.xy_vel)
        self.x = xpos
        self.y = ypos

    def move_piece(self, move):
        move1 = move[0:2]
        move2 = move[2:4]
        

        self.move_square(move1)
        self.grab_piece()
        self.move_square(move2)
        self.drop_piece()
    
    def move_square(self, move):
        letter = move[0:1]
        number = move[1:2]

        if(letter == 't'):
            x_pos = 0
        else:
            x_pos = (self.letterDictionary[letter]-1)*self.square_size+self.x_offset
        
        y_pos = (int(number)-1)*self.square_size+self.y_offset


        self.move_to_xy(x_pos, y_pos)
        
    def calculate_fen_position(self):
        #TODO Move extruder to where the picture needs to be taken from, take the picture, run opencv analysis, and convert to FEN
        print("Taking a look at the board...")

        self.move_to_z(self.vision_height)

        pictures = [None]*4

        for i, p in enumerate(self.quadrant_pos):
            self.move_to_xy(p[0], p[1])
            pictures[i] = take_picture()
            cv.imwrite(f"Q{i+1}.jpg", pictures[i])

        print("Analyzing...")

        pieces = self.get_img_pieces(pictures)

        self.move_to_z(self.move_height)

        pieces_array = self.pieces_to_arr(pieces)

        #Insert opencv magic here
        
        FEN = random_FEN.start() #For testing
        return [FEN, pieces_array]
        #example FEN (starting position): "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def pieces_to_arr(self, pieces):
        arr = np.zeros([8,8], dtype=str)
        for p in pieces:
            j = 7-(int(self.letterDictionary[p["square"][0:1]])-1)
            i = 7-(int(p["square"][1:2])-1)

            arr[i,j] = p["piece"]

            if(p["piece"] == "knight"):
                arr[i,j] = 'n'

            if(p["color"] == "white"):
                arr[i,j] = arr[i,j].upper()
            
        
        print(arr)
        return arr

    
    def get_img_pieces(self, imgs):
        pieces = []
        for i in range(4):
            img = imgs[i]

            temp_dict = {}

            x_off = self.quadrant_params["x_offset"][i]
            y_off = self.quadrant_params["y_offset"][i]
            s_size = self.quadrant_params["square_size"][i]
            s_off = self.quadrant_params["square_offset"][i]


            img = crop_quadrant(img, x_off, y_off, s_size)
            extract_HSV_channels(cv.cvtColor(img,cv.COLOR_BGR2HSV), suffix=str(i))

            image_center = [0,0]
            image_center[0] = (s_size*2+y_off)
            image_center[1] = s_size*2+x_off

            for p in self.piece_color_dict.keys():
                cntrs = get_contours(img, self.piece_color_dict[p])
                for c in cntrs:
                    
                    center = get_centroid(c)
                    #cv.circle(img, center, 10, (255, 0, 0))
                    #cv.imwrite("circle.jpg", img)
                    square = self.square_from_centroid(center, x_off, y_off, s_size)
                    letter = (square[0] + s_off[0]+1)
                    letter = list(self.letterDictionary.keys())[list(self.letterDictionary.values()).index(letter)]
                    number = square[1] + s_off[1] + 1

                    pos =  letter + str(number)
                    area = cv.contourArea(c)
                    if(pos in temp_dict and temp_dict[pos] > area):
                        continue

                    center_dist = [0, 0]
                    center_dist[0] = center[0] - image_center[0]
                    center_dist[1] = center[1] - image_center[1]

                    rect_width = 20
                    rect_length = math.sqrt(center_dist[0]**2+center_dist[1]**2)/5 + 20
                    piece_dist = 25
                    center_angle = math.atan2(center_dist[1], center_dist[0])
                    rect_angle = math.pi/2 - center_angle
                    rx = rect_width/2*math.cos(rect_angle)
                    ry = rect_width/2*math.sin(rect_angle)

                    rmx1 = center[0]-piece_dist*math.cos(center_angle)
                    rmy1 = center[1]-piece_dist*math.sin(center_angle)
                    rmx2 = center[0]-rect_length*math.cos(center_angle)
                    rmy2 = center[1]-rect_length*math.sin(center_angle)

                    p1 = (int(rmx1-rx), int(rmy1+ry))
                    p2 = (int(rmx1+rx), int(rmy1-ry))
                    p3 = (int(rmx2+rx), int(rmy2-ry))
                    p4 = (int(rmx2-rx), int(rmy2+ry))

                    rect_mask = np.zeros(img[:,:,2].shape, dtype=img[:,:,2].dtype)
                    cv.drawContours(rect_mask, [np.array([p1, p2, p3, p4])], -1, 255, thickness=-1)
                    rect_mask = cv.bitwise_and(img[:,:,2], img[:, :, 2], mask=rect_mask)
                    
                    sum = 0
                    pix = 0
                    for i in range(rect_mask.shape[0]):
                        for j in range(rect_mask.shape[1]):
                            if(rect_mask[i, j] > 0):
                                sum += rect_mask[i,j]
                                pix += 1

                    cv.drawContours(img, [c], -1, (0,255,0), thickness=3)

                    #cv.imwrite(f"cntr{i}.jpg", img)

                    temp_dict[pos] = area

                    color = "black"
                    if(sum/pix > 60):
                        color = "white"

                    pieces.append({
                        "piece":p,
                        "square": pos,
                        "color": color
                    })
        return pieces
                

    
    def square_from_centroid(self, center, x_offset, y_offset, square_size):
        number = 3-int((center[0]-y_offset)/square_size)
        letter = int((center[1]-x_offset)/square_size)
        return (letter, number)
    
    def get_legal_moves(fen_state):
        stockfish.set_fen_position(fen_state)
        stockfish._put("go perft 1")
        legal_moves = []
        while True:
            l = stockfish._read_line()
            if(l[0:4] == "Node"):
                return False
            else:
                move = l[0:4]
                legal_moves += [str(move)]
                    return True
        return legal_moves


    def grab_piece(self):
        self.move_to_z(self.grab_height)
        print("Telling the raspi to close the claw...")  #TODO Open a serial connection, login, and run the close.py script
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("python3 Desktop/light-blue/close.py")
        time.sleep(2)
        self.move_to_z(self.move_height)

    def drop_piece(self):
        self.move_to_z(self.grab_height)
        print("Telling the raspi to open the claw...")  #TODO Open a serial connection, login, and run the open.py script
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("python3 Desktop/light-blue/open.py")
        time.sleep(2)
        self.move_to_z(self.move_height)