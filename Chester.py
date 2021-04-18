#You must run this with: sudo -E python3 Chester.py
from stockfish import Stockfish         #Check AI.py for info on this \/
stockfish = Stockfish("/home/michael/Desktop/light-blue/stockfish_20090216_x64",parameters={"Threads": 2})
import serial   #Confusingly, the package for this is pySerial not serial
import time
import sys
import paramiko
import random_FEN
import cv_cmods

def move_piece(move):
    letter = move[0:1]
    number = move[1:2]
    letter2 = move[2:3]
    number2 = move[3:4]
    letterDictionary = {
        "a":"12.7",
        "b":"38.1",
        "c":"63.5",
        "d":"88.9",
        "e":"114.3",
        "f":"139.7",
        "g":"165.1",
        "h":"190.5",
    }
    y_pos = (int(number)-1)*25.4+12.7
    x_pos = letterDictionary[letter]

    y_pos2 = (int(number2)-1)*25.4+12.7
    x_pos2 = letterDictionary[letter2]

    ser.write(b'G1 F2750\r\n')
    time.sleep(1)

    gcode_string = str.encode("G1 X"+str(x_pos)+" Y"+str(y_pos)+"\r\n")
    ser.write(gcode_string)
    time.sleep(3)

    grab_piece()

    gcode_string2 = str.encode("G1 X"+str(x_pos2)+" Y"+str(y_pos2)+"\r\n")
    ser.write(gcode_string2)
    time.sleep(3)

    drop_piece()
    time.sleep(1)

def calculate_fen_position():
    #TODO Move extruder to where the picture needs to be taken from, take the picture, run opencv analysis, and convert to FEN
    print("Taking a look at the board...")
    ser.write(b'G1 Z25\r\n')     #Move the Z axis up and out of the way of the pieces
    time.sleep(2)
    ser.write(b'G1 X60 Y40\r\n')     
    take_picture()
    time.sleep(3)
    ser.write(b'G1 X140 Y40\r\n')     
    take_picture()
    time.sleep(3)
    ser.write(b'G1 X140 Y100\r\n')     
    take_picture()
    time.sleep(3)
    ser.write(b'G1 X60 Y100\r\n')     
    take_picture()
    time.sleep(3)

    print("Analyzing...")
    ser.write(b'G1 Z15\r\n')   
    time.sleep(2)
    #Insert opencv magic here
    
    FEN = random_FEN.start() #For testing
    return FEN
    #example FEN (starting position): "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("raspberrypi", username="pi", password="chester")
#ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("python3 Desktop/light-blue/close.py")
def grab_piece():
    ser.write(b'G1 Z0\r\n')     #Move the Z axis back to 0 (to grab the piece)
    time.sleep(3)
    print("Telling the raspi to close the claw...")  #TODO Open a serial connection, login, and run the close.py script
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("python3 Desktop/light-blue/close.py")
    time.sleep(2)
    ser.write(b'G1 Z15\r\n')     #Move the Z axis up and out of the way of the pieces
    time.sleep(1)

def drop_piece():
    ser.write(b'G1 Z0\r\n')     #Move the Z axis back to 0 (to drop the piece)
    time.sleep(3)
    print("Telling the raspi to open the claw...")  #TODO Open a serial connection, login, and run the open.py script
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("python3 Desktop/light-blue/open.py")
    time.sleep(2)
    ser.write(b'G1 Z15\r\n')     #Move the Z axis up and out of the way of the pieces
    time.sleep(1)
    

#Assumes that chessboard is 8x8" and that z height is set so the claw can pick up pieces 
player = input("Would you like to play white or black pieces? (Type w or b)")
print("Standby...")

#On my laptop, port is '/dev/ttyACM0'
#On my desktop, using wsl, port should be '/dev/ttyS#' (where # is the COM port) but I can't get it to work, but setting it to tty# let's it run if you just wanna test
ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
ser.write(b'G92 Z0\r\n')     #Tell the printer that its current Z position is 0
time.sleep(1)
ser.write(b'G1 Z15\r\n')     #Move the Z axis to 10 (to clear the pieces)
time.sleep(1)
ser.write(b'G28 X0 Y0\r\n')  #Home the X and Y axis because their position is unknown 
time.sleep(1)

if(player == "w"):
    input("Make your first move, then press Enter")
else:
    print("I'm making my first move")
    time.sleep(10)
    move_piece("d2d4")
    input("Make your move, then press Enter")

winner = False      #Need to check if there's a winner after each move and if so: break the loop
while(not winner):
    current = calculate_fen_position()        #This takes a picture and analyzes it, then generates the fen position of the board and returns it as a string
    print(current)
    stockfish.set_fen_position(current)
    print(stockfish.get_board_visual())
    time.sleep(1)
    move = str(stockfish.get_best_move())
    if(move == "None"):
        print("No possible move or something")
        exit()
    print("Moving " + move)
    move_piece(move)
    input("Make your move, then press Enter")

ser.close()
