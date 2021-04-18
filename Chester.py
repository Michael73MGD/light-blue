#You must run this with: sudo -E python3 Chester.py
from stockfish import Stockfish         #Check AI.py for info on this \/
stockfish = Stockfish("/home/jack/projects/light-blue/stockfish_20090216_x64",parameters={"Threads": 2})
import serial   #Confusingly, the package for this is pySerial not serial
import time
import sys
import paramiko
import random_FEN
import urllib
from cv_cmds import take_picture
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

    quadrant_pos = [(60, 15), (140, 15), (140, 100), (60, 100)]

    letterDictionary = {
            "a":1,
            "b":2,
            "c":3,
            "d":4,
            "e":5,
            "f":6,
            "g":7,
            "h":8,
        }
    x_offset = 12.7
    y_offset = 5
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
        letter = move[0:1]
        number = move[1:2]
        letter2 = move[2:3]
        number2 = move[3:4]
        

        y_pos = (int(number)-1)*self.square_size+self.y_offset
        x_pos = (self.letterDictionary[letter]-1)*self.square_size+self.x_offset

        y_pos2 = (int(number2)-1)*self.square_size+self.y_offset
        x_pos2 = (self.letterDictionary[letter2]-1)*self.square_size+self.x_offset

        self.move_to_xy(x_pos, y_pos)
        self.grab_piece()
        self.move_to_xy(x_pos2, y_pos2)
        self.drop_piece()

        
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
        self.move_to_z(self.move_height)

        #Insert opencv magic here
        
        FEN = random_FEN.start() #For testing
        return FEN
        #example FEN (starting position): "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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