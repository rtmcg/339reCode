import serial
import time as t
import numpy as np
import matplotlib.pyplot as plt

# get value and arraysize set by user
value = 100
arraySize = 500

serialPort = serial.Serial() # create a serial instance
serialPort.baudrate = 9600 # set the baud rate
serialPort.port = "COM4" # COM? set the com port used on arduino
print(serialPort) # print serial port specifications

serialPort.open() # open the serial port, The state of rts and dtr is applied, dtr is what can reset the arduino

dataRead = False # set to false, until loop ends
data = [] # list to fill up with data from arduino

while dataRead == False: # while the wanted amoutn of data has yet to be read
    serialPort.write(chr(value).encode(encoding = 'latin-1')) # writing to the serial port, chr gets the character that represents the unicode value, then encodes to bytes, latin-1 is used since this gives single bytes for values 0-255, whereas utf-8 does not for all those values
    t.sleep(0.1) # pause between writing and reading
    inByte = serialPort.in_waiting # checks for bytes in the input buffer
    #This loop reads in data from the array until byteCount reaches the array size (arraySize)
    byteCount = 0 # used to check the byte count is less than the array size, this may be not needed, as explained in lab2_6_2_other_option.py
    while (inByte > 0) & (byteCount < arraySize): # bitwise &, while returns true with both values
        dataByte = serialPort.read().decode() # encoding = 'latin-1' may be needed, read and decode bytes from the serial port
        byteCount = byteCount + 1 # could use byteCount += 1, increment the byte count
        data = data + [dataByte] # adds data to data list could use data += [dataByte] or data.extend(dataByte) also (or option in other file)
    if byteCount == arraySize: # if the number of bytes reaches the set array size
        dataRead = True # end the loop
        
serialPort.close() # close the serial port

dataOut = np.zeros(arraySize) # create an np array of zeros, shape of arraysize
arrayIndex = range(arraySize) # used in the for loop and plot, range of array size, this doesn't create a list like in python 2

#Transform unicode encoding into integers
for i in arrayIndex: # loop through range of array size
    dataOut[i] = ord(data[i]) # ord returns the number representing the unicode of character in data array, assigns zeros in dataout to this
    
#Plot your analog output!
f1 = plt.figure() # create a figure, may not be needed with automatic graphics backend set on spyder
plt.plot(arrayIndex, dataOut, 'o') # plot of arrayindex and dataout, arrayindex is not needed since it's just the index
plt.xlabel("array index") # plot label for x
plt.ylabel("8-bit rounded voltage reading") # plot label for y

print('mean:', np.mean(dataOut)) # prints the mean of dataout
