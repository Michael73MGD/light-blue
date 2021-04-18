from flask import Flask, render_template
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
app = Flask(__name__)

FEN = "FEN test"


ser = serial.Serial('/dev/ttyACM1', 115200)



chester = Chester(ser)

Chester.check_legal_move("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2", "e4")

def signal_handler(sig, frame):
    chester.drop_piece()
    ser.write(b'G1 Z0\r\n')  
    time.sleep(1)
    print("done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Assumes that chessboard is 8x8" and that z height is set so the claw can pick up pieces 

# while True:
    # move = input("Enter a square to move to: ")
    # if(move == "grab"):
    #     chester.grab_piece()
    # elif(move == "drop"):
    #     chester.drop_piece()
    # else:
    #     chester.move_square(move)

input("Make your first move, then press Enter")
# else:
#     print("I'm making my first move")
#     time.sleep(10)
#     chester.move_piece("d2d4")
#     input("Make your move, then press Enter")

winner = False      #Need to check if there's a winner after each move and if so: break the loop
while(not winner):
    FEN = chester.calculate_fen_position()  
    potential_moves = chester.get_legal_moves(FEN)

    @app.route("/chester")
        def bootstrapTest():
        #return render_template("bootstrapTest.html")
        return render_template('bootstrapTest.html', FEN=FEN)   #{{FEN}}






@app.route("/")
def home():
    return render_template("home.html")

@app.route("/move")
def salvador():
    return render_template("movingTest.html")

@app.route("/chester")
def bootstrapTest():
    #return render_template("bootstrapTest.html")
    return render_template('bootstrapTest.html', FEN=FEN)   #{{FEN}}     to access in html

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return jsdata
    #in JS: 
    #$.post( "/postmethod", {
    #javascript_data: data 
    #});




if __name__ == "__main__":
    app.run(debug=True)