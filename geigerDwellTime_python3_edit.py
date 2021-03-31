import matplotlib.pyplot as p
import numpy as n
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
    def __init__(self,verbose =0):
        self.verbose = verbose
        if self.verbose: print("verbose output active")
        for i in range(2,10):
            device = "COM%d" % (i)
            print(("Trying '%s'"%(device)))
            try:
                self.handle = serial.Serial(device,baudrate=9600,timeout=2.0,)
                print("Found device at %s" % (device))
                break
            except:
                continue
        tries = 0
        if tries <5:
            tries += 1
            self.handle.dtr = 0
            self.handle.dtr = 1
            if self.verbose: print("Clearing I/O buffer")
            self.handle.timeout = 0
            resp = self.handle.read(1048756)
            if self.verbose: print(("Cleared %d bytes of junk" % (len(resp))))
            if self.verbose: print("Waiting for wakeup")
            self.handle.timeout = 2;
            #resp = self.handle.readline() 
            resp = self.handle.readline().decode()#.split('\r\n')#[0]
            if "Geiger 2018\r\n" == resp:
                print("Got the expected response: ''%s'', Arduino initialized, waiting for events." % repr(resp))
                self.handle.timeout = 2000      # 2000s because we want to wait a long time when doing readline            
                return
            print("Unexpected response: ''%s'', going to retry..." % repr(resp))
        elif tries == 5 :
            print(("Giving up on device ''%s''"%(device)))
            self.handle.close()
            raise RuntimeError("No Geiger 2018 programmed device found")
     
    def getInterval(self):
        """
        Returns the duration of next interval between events in microseconds.  
        It may raise an exception if an overrun is detected.  
        An overrun happens when events arise to quickly and the Arduino cannot
        get data out fast enough to prevent data loss.
        """
        #resp = self.handle.readline()
        resp = self.handle.readline().decode('latin-1').split('\r\n')[0]  
        if self.verbose: print("Verbose got resp:", repr(resp), "\n")
        if "\r\n" != resp[-2:]:
            if "\r" == resp[-1:]: # Stupid readline, do your job ... one @##$@ job!
                resp2 = self.handle.read(1)
                if "\n" != resp2:
                    self.handle.close()
                    raise RuntimeError("Incomplete line read")
                resp = resp + resp2
        if "Overrun\r\n" == resp:
            self.handle.close()
            raise RuntimeError("Arduino reports overrun")
        #return int(resp)
        return int(resp) 
 
    def backlog(self):
        """
        Returns the number of bytes which are waiting in the input queue.  
        This is important because if the Arduino is producing a great deal of data, 
        even though the Arduino has faithfully sent all the data to the computer, the 
        OS may toss the data if no one is picking it up at the same rate.
        """
        return self.handle.inWaiting
    
    def closePort(self):
        self.handle.close()
        print("Port is now closed")
        return
     


arduino = Arduino(verbose=0) # Initialize an instance of the Arduino class, default 0


'''****************  THESE ARE THE ONLY VALUES YOU NEED TO CHANGE  *************************'''

intervalNum = 100     # Number of intervals to be recorded
replicaNum = 3       # Number of replicas to record

'''*****************************************************************************************'''
 
 
intervals = n.ones((replicaNum,intervalNum)) # Declare intervals array, and fill it with ones

           

for replica in range(replicaNum):   # Pack interval data into intervals array, and report to user
    for interval in range(intervalNum):    
        intervals[replica,interval] = arduino.getInterval() # GetInterval() has a 2000 second timeout, but will finish once a click happens 
        print("\nReplica # %d. Interval # %d. Interval length received: %d" % ((replica+1), (interval+1), intervals[replica,interval]))

for i in range(replicaNum): # Histogram graphing section, to visually check if the data is decent.
    p.hist(intervals[i,:],)
    p.title("Replica #%d" % (i+1))
    i+=1
    
    
# Save the file and close the serial device
fileName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+"_int"+str(intervalNum)+"_rep"+str(replicaNum)+"_DWELL_TIME_DATA.csv"
print("Data saved as ", fileName)
#n.savetxt(fileName,intervals, delimiter =",")
arduino.closePort()
