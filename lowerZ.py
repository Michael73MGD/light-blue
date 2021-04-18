import serial
import time
import sys

#Template: 
#ser.write(b'G\r\n')
#time.sleep(1)

ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
amt = sys.argv[1]
ser.write(b'G92 Z0\r\n')
time.sleep(1)
ser.write(bytes(f'G1 Z{amt}\r\n F4500', 'utf-8'))
time.sleep(1)

ser.close()
