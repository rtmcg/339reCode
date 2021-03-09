import serial
import time as t
import numpy as np
import matplotlib.pyplot as plt

value = 130
arraySize = 500

serialPort = serial.Serial()
serialPort.baudrate = 9600
serialPort.port = "COM3" # COM?
print(serialPort)

serialPort.open()

dataRead = False
dataOut = [] # was data

while dataRead == False:
    serialPort.write(chr(value).encode(encoding = 'latin-1')) # other options are given in lab2_6
    t.sleep(0.1)
    inByte=serialPort.in_waiting # changed from inWaiting() again
    #This loop reads in data from the array until len(dataOut) reaches the array size (arraySize)
    while inByte > 0: # (inByte > 0) & (byteCount < arraySize): not needed both when already have dataRead to stop the loop
        dataByte = serialPort.read().decode()
        dataOut.append(ord(dataByte)) # was data = data + [dataByte] #Transform unicode encoding into integers
        if len(dataOut) == arraySize: # was byteCount == arraySize:
            dataRead = True
            break
        
serialPort.close()

#Plot your analog output!
f1=plt.figure()
plt.plot(dataOut, 'o') # index plotting is automatic, was (arrayIndex, dataOut, 'o')
plt.xlabel("array index")
plt.ylabel("8-bit rounded voltage reading")

print('mean:', np.mean(dataOut))  
