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
from Chester import Chester

#On my laptop, port is '/dev/ttyACM0'
#On my desktop, using wsl, port should be '/dev/ttyS#' (where # is the COM port) but I can't get it to work, but setting it to tty# let's it run if you just wanna test
ser = serial.Serial('/dev/ttyACM0', 115200)

def signal_handler(sig, frame):
    ser.write(b'G1 Z0\r\n')  
    time.sleep(1)
    print("done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

chester = Chester(ser)



#Assumes that chessboard is 8x8" and that z height is set so the claw can pick up pieces 
player = input("Would you like to play white or black pieces? (Type w or b)")
print("Standby...")

if(player == "w"):
    input("Make your first move, then press Enter")
else:
    print("I'm making my first move")
    time.sleep(10)
    chester.move_piece("d2d4")
    input("Make your move, then press Enter")

winner = False      #Need to check if there's a winner after each move and if so: break the loop
while(not winner):
    current = chester.calculate_fen_position()        #This takes a picture and analyzes it, then generates the fen position of the board and returns it as a string
    print(current)
    stockfish.set_fen_position(current)
    print(stockfish.get_board_visual())
    time.sleep(1)
    move = str(stockfish.get_best_move())
    if(move == "None"):
        print("No possible move or something")
        exit()
    print("Moving " + move)
    chester.move_piece(move)
    input("Make your move, then press Enter")

ser.close()

