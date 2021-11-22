import serial
import time as t
import numpy as np
import matplotlib.pyplot as plt

value = 200 # set by user
maxCount = 100 # set by user
serialPort = serial.Serial() # serial instance
serialPort.baudrate = 9600 # baudrate set
serialPort.port = "COM4" # Remember that you may need to change the COM port.
print(serialPort) # serial port info printed
serialPort.open() # open serial port
dataRead = False # used in loop, until enough data is read, is false
data = [] # data list to store data read
numCount = 0 # counter to stop loop when maxcount is reached
timeCount = [] # timecount list of times counts are detected
startTime = t.time() # start the timer

while dataRead == False: # loop while data read is below max counts
    serialPort.write(chr(value).encode()) # returns character of unicode value, encodes to bytes, write to serial port
    inByte = serialPort.in_waiting # checks for bytes in input buffer
    if inByte > 0: # if bytes are in input buffer
        serialStringIn = serialPort.readline().decode() # read a line from serial port and decode bytes to python string
        if serialStringIn[0] == 'C': # if first value in serial string in is C 
            numCount += 1 # was = numCount + 1, add 1 to numcount
            to = t.time() - startTime # find the time since the start time
            print("click number:", numCount) # print the count number
            print("time-stamp (s):", to) # print the time stamp
            timeCount.append(to) # append time stamp to time count list
            if numCount == maxCount: # if count number is equal to max counts
                dataRead = True # data read is tru and loop is exitted
                
serialPort.close() # close the port
maxT = max(timeCount) # find the max timecount (the last)
numZeros = 1000 # number of zeros set
timeZeros = np.linspace(0, maxT, numZeros) # make an array 0 to maxT with numzeros length
zeroValues = np.zeros(numZeros) # make an array of zeros with numzeros shape
oneValues = np.ones(maxCount) # make and array of ones with maxcount shape
#f1 = plt.figure() # not needed, plotting is automatic
plt.plot(timeCount, oneValues, 'o') # plot one values for time counts
plt.plot(timeZeros, zeroValues, 'o') # plot zerovalues for timezeros
plt.xlabel("time (s)") # plot x label
plt.ylabel("Spike") # plot y label set
#plt.show() # not needed, plotting is automatic