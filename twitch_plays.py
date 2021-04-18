from twitch_plays_hackru import TwitchPlaysOnline, TwitchPlaysOffline

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

potential_moves = []  #An array of strings of legal moves (ex. ["a4e4"])

#On my laptop, port is '/dev/ttyACM0'
#On my desktop, using wsl, port should be '/dev/ttyS#' (where # is the COM port) but I can't get it to work, but setting it to tty# let's it run if you just wanna test
ser = serial.Serial('/dev/ttyACM0', 115200)

chester = Chester(ser)

def signal_handler(sig, frame):
    chester.drop_piece()
    ser.write(b'G1 Z0\r\n')  
    time.sleep(1)
    print("done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Assumes that chessboard is 8x8" and that z height is set so the claw can pick up pieces 
input("Make your first move, then press enter")
print("Standby...")


winner = False      #Need to check if there's a winner after each move and if so: break the loop
while(not winner):
    current = chester.calculate_fen_position()  
    potential_moves = chester.get_legal_moves(current)
    twitch_options = {
    "PASS": "oauth:***",
    "BOT": "Chester",
    "CHANNEL": "psych_its_mike",
    "OWNER": "psych_its_mike",
    "OPTIONS": potential_moves,
    "VOTE_INTERVAL": 5
    }
    tPlays = TwitchPlaysOnline(**twitch_options)

    time.sleep(30)
    result = tPlays.vote_result()
    print('And the winning move is: '+ str(result))
    
    chester.move_piece(result)
    input("Make your move and press enter")


ser.close()







