#Import pySerial library
import serial
#another option to send bytes
import struct
#Import time library
import time as t
#8-bit value to be written to PWB pin
value = 255
#Initialize serial port and label port ``serialPort"
serialPort = serial.Serial()
#Set baud-rate to 9600
serialPort.baudrate = 9600
#Set port name to that of Arduino-need to replace ? with correct COM port number
serialPort.port = "COM3" # COM?
#Prints port specifications
print(serialPort)
#Open serial port
serialPort.open()
#Send write values to serial port until response character "W" is received
dataRead = False
while dataRead == False:
    serialPort.write(chr(value).encode(encoding = 'latin-1')) # encode to bytes, str.encode(encoding="utf-8", errors="strict") chr() in python 3 is unichr() in python 2, encoding = 'ISO-8859-1' also works
    #serialPort.write(value.to_bytes(1, byteorder='big')) # this works also, int.to_bytes(length, byteorder, *, signed=False)
    #serialPort.write(bytes([value])) # also works bytes([source[, encoding[, errors]]])
    #serialPort.write(struct.pack('B', value)) # also works struct.pack(format, v1, v2, ...)
    t.sleep(0.1)
    inByte=serialPort.in_waiting #inWaiting() is deprecated
    if inByte > 0:
        serialStringIn = serialPort.readline().decode() # decode from bytes  bytes.decode(encoding="utf-8", errors="strict")
        if serialStringIn[0] == 'W':
            dataRead = True
#Close serial port
serialPort.close() # this could be included after a try statement in case the loop throws an error, so it could still close