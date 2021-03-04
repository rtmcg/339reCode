import serial
import time as t
import numpy as np
import matplotlib.pyplot as plt

value=200 #200
maxCount=100 #100
serialPort=serial.Serial()
serialPort.baudrate=9600
serialPort.port="COM3" #Remember that you may need to change the COM port.
print(serialPort)
serialPort.open()
dataRead=False
data=[]
numCount=0
timeCount=[]
startTime=t.time()
while (dataRead==False):
    serialPort.write(chr(value).encode())
    inByte=serialPort.inWaiting()
    if(inByte>0):
        serialStringIn=serialPort.readline().decode()
        if(serialStringIn[0]=='C'):
            numCount=numCount+1
            to=t.time()-startTime
            print("click number:", numCount)
            print("time-stamp (s):", to)
            timeCount.append(to)
            if(numCount==maxCount):
                dataRead=True
serialPort.close()
maxT=max(timeCount)
numZeros=1000
timeZeros=np.linspace(0, maxT, numZeros)
zeroValues=np.zeros(numZeros)
oneValues=np.ones(maxCount)
f1=plt.figure()
plt.plot(timeCount, oneValues, 'o')
plt.plot(timeZeros, zeroValues, 'o')
plt.xlabel("time (s)")
plt.ylabel("Spike")