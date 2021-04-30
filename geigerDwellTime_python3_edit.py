import matplotlib.pyplot as plt
import numpy as np
import serial
#import os
import datetime

"""
This is a simple class which attempts to find an Arduino which has
the Geiger-339 sketch loaded.  It has two methods of interest:
    
backlog() which returns number of bytes waiting to be read.
 
getInterval() which returns a single interval measurement from the queue.

Be sure to connect the geiger to pin 2 (this is the pin to which an Arduino interrupt is hardwired)

Scroll down for options regarding replica and interval quantities

Reviewed and updated Summer 2018
"""

class Arduino: # Definition of class made to read geiger data sent from Arduino 
    def __init__(self, verbose = 0):
        self.verbose = verbose # create verbose instance attribute
        if self.verbose: print("verbose output active") # print if verbose 
        #for i in range(2,10):
        #device = "COM%d" % (i)
        device = "COM4" # set by user, from what's on arduino
        #print("Trying '%s'"%(device))
        print(f"Trying '{device}'") # print trying the port set
        try:
            #self.handle = serial.Serial(device, baudrate = 9600, timeout = 2.0,)
            self.handle = serial.Serial(device, baudrate = 9600, timeout = 2.0) # seral port instance, with baudrate and timeout set to 2, waits until number of requested bytes are received, or until timeout expires
            #print("Found device at %s" % (device))
            print(f"Found device at {device}") # print found devide if handle worked
            #break
        except: # if try doesn't work
            print('Device not found') # print out
            #continue
        tries = 0 # tries initialized to 0
        if tries < 5: # if tries less than 5
            tries += 1 # increment tries
            self.handle.dtr = 0 # set dtr to 0
            self.handle.dtr = 1 # then to 1
            if self.verbose: print("Clearing I/O buffer") # print out
            self.handle.timeout = 0 # set timeout to 0
            resp = self.handle.read(1048756) # read this many bytes to clear buffer
            #if self.verbose: print("Cleared %d bytes of junk" % (len(resp)))
            if self.verbose: print(f"Cleared {len(resp)} bytes of junk") # print how many bytes cleared
            if self.verbose: print("Waiting for wakeup") # print out
            #self.handle.timeout = 2;
            self.handle.timeout = 2 # timeout set to 2 again
            #resp = self.handle.readline() 
            resp = self.handle.readline().decode()#.split('\r\n')#[0] # readline from serial port, then decode bytes
            if "Geiger 2018\r\n" == resp: # if the response is this
                #print("Got the expected response: ''%s'', Arduino initialized, waiting for events." % repr(resp))
                print(f"Got the expected response: ''{repr(resp)}'', Arduino initialized, waiting for events.") # print out with response, with repr which leaves in \r\n
                self.handle.timeout = 2000      # 2000s because we want to wait a long time when doing readline            
                return # return nothing
            #print("Unexpected response: ''%s'', going to retry..." % repr(resp))
            print(f"Unexpected response: ''{repr(resp)}'', going to retry...") # print this if expected response was not obtained
        elif tries == 5: # if tries is 5
            #print("Giving up on device ''%s''"%(device))
            print(f"Giving up on device ''{device}''") # print giving up
            self.handle.close() # close serial port
            raise RuntimeError("No Geiger 2018 programmed device found") # raise error no device found
     
    def getInterval(self): # function gets interval between counts
        """
        Returns the duration of next interval between events in microseconds.  
        It may raise an exception if an overrun is detected.  
        An overrun happens when events arise to quickly and the Arduino cannot
        get data out fast enough to prevent data loss.
        """
        #resp = self.handle.readline()
        resp = self.handle.readline().decode('latin-1').split('\r\n')[0] # readline from serial port, decode the single bytes with latin-1, split on \r\n and take the first element
        if self.verbose: print("Verbose got resp:", repr(resp), "\n") # if verbose, print response
        if "\r\n" != resp[-2:]: # if resp does not end with \r\n
            if "\r" == resp[-1:]: # Stupid readline, do your job ... one @##$@ job! # if resp ends with \r (\n is left out)
                resp2 = self.handle.read(1) # read one byte from serial port
                if "\n" != resp2: # if it isn't \n
                    self.handle.close() # close serial port
                    raise RuntimeError("Incomplete line read") # raise error
                resp = resp + resp2 # add \n to resp
        if "Overrun\r\n" == resp: # if resp is this
            self.handle.close() # close serial port
            raise RuntimeError("Arduino reports overrun") # raise error
        return int(resp) # return resp as int
 
    def backlog(self): # as described below
        """
        Returns the number of bytes which are waiting in the input queue.  
        This is important because if the Arduino is producing a great deal of data, 
        even though the Arduino has faithfully sent all the data to the computer, the 
        OS may toss the data if no one is picking it up at the same rate.
        """
        #return self.handle.inWaiting # should be inWaiting()
        return self.handle.in_waiting # returns bytes in input buffer
    
    def closePort(self): # close port method
        self.handle.close() # close serial port
        print("Port is now closed") # print out
        return # return nothing
     


arduino = Arduino(verbose = 1) # Initialize an instance of the Arduino class, default 0


'''****************  THESE ARE THE ONLY VALUES YOU NEED TO CHANGE  *************************'''

intervalNum = 100     # Number of intervals to be recorded
replicaNum = 1       # Number of replicas to record

'''*****************************************************************************************'''
 
 
intervals = np.ones((replicaNum,intervalNum)) # Declare intervals array, and fill it with ones

           

for replica in range(replicaNum):   # Pack interval data into intervals array, and report to user
    for interval in range(intervalNum): # loops through interval number
        intervals[replica,interval] = arduino.getInterval() # GetInterval() has a 2000 second timeout, but will finish once a click happens 
        #print("\nReplica # %d. Interval # %d. Interval length received: %d" % ((replica+1), (interval+1), intervals[replica,interval]))
        print(f"\nReplica # {(replica+1)}. Interval # {(interval+1)}. Interval length received: {intervals[replica,interval]}") # prints interval and replica info

for i in range(replicaNum): # Histogram graphing section, to visually check if the data is decent.
    plt.hist(intervals[i,:],) # plot histogram of intervals
    #p.title("Replica #%d" % (i+1))
    plt.title(f"Replica #{i+1}") # plot title
    i += 1
    
    
# Save the file and close the serial device
fileName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_int" + str(intervalNum) + "_rep" + str(replicaNum) + "_DWELL_TIME_DATA.csv" # create file name with date, time and interval and replica info
print("Data saved as ", fileName) # print out save
#np.savetxt(fileName,intervals, delimiter =",") # save if uncommented
arduino.closePort() # close serial port
