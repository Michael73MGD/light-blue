import serial
import time

#Template: 
#ser.write(b'G\r\n')
#time.sleep(1)

ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
ser.write(b'G92 Z15\r\n')
time.sleep(1)
ser.write(b'G1 Z0\r\n')
time.sleep(1)

ser.close()
