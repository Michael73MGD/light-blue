import serial
import time
import sys

#Template: 
#ser.write(b'G\r\n')
#time.sleep(1)

ser = serial.Serial('/dev/ttyACM0', 115200)
amt = sys.argv[1]
time.sleep(2)
print("hi")
ser.write(bytes(f'G92 Z{amt}\r\n F6000', 'utf-8'))
time.sleep(1)
ser.write(b'G1 Z0\r\n')
time.sleep(1)

ser.close()
