# -*- coding: utf-8 -*-
'''
Created on Mon Jan 16 09:21:34 2017
Reviewed and updated Summer 2018

This file contains a class with methods, 3 functions, and a line to initialize an object based on the class.

It will connect to the Arduino code, tell the Arduino what time period the user wants, and receive the counts per interval 
that the Arduino records fro the Geiger counter. Every time a new data point is recorded, it is plotted into a histogram figure,
which is then re-plotted every period interval. The console should scroll with the updates, giving a fascimile of animation.

Be sure to connect the geiger to pin 2 (this is the pin to which an Arduino interrupt is hardwired))

Scroll to the bottom to see the rc variable (representing the instance of the class), where you can change some settings.

'''

# ==============================================================================
# Import libraries
# ==============================================================================

import matplotlib.pyplot as p
import numpy
import serial
import datetime

# ==============================================================================
# Definition of class that has been made to read geiger data sent from Arduino.
# An instance of this class will be called when the geiger() function is called.
# ==============================================================================

class GeigerArduino:
    def __init__(self,verbose=1):   # Verbose mode will let give you a lot more information, and is best used in conjunction with debug==2 in Arduino, default = 0
        self.verbose = verbose      # Sets the instance attribute equal to the user's input or the default value
        if verbose: print("introArduino class creator: Verbose mode activated")
        for i in range(2,10):       # Iterate through a series of port options, trying to see if the Arduino is connected
            device = "COM%d" % (i)  # Encode current port option
            if verbose: print(("Trying '%s'"%(device)))
            try:                    # If there is an exception when the serial.Serial() method is called, the script won't crash, and instead will try other things
                self.device = serial.Serial(device,baudrate=9600,timeout=2.0,)  # Initialize an isntance of PySerial's serial connection, with the variable name self.device (in this case it'll be a.handle())
                if verbose: print("Found device at %s" % (device))
                break
            except:                     # Code within this will execute right after an exception happens in the try part
                continue
        buf = self.device.read(10000)   # Clean out the buffer by reading bytes
        if self.verbose: print(("cleared %d bytes"%(len(buf))))
        self.device.setDTR(1);          # Reboot Arduino
        self.device.setDTR(0);          # DTR is a holdover from old-school serial communications. Stands for Data Terminal Ready
        self.device.setDTR(1);
        exception_count = 0             # Init an exception counter
        attempts = 0                    #  Init an attempt counter
        while True:                     # Infinite loop, is controlled by the previous two counters
            try:    
                if "HELLO" == self.getResp(): # Calls the getResp() method, which performs a readline(). This is the Python trying to handshake with Arduino
                    if verbose: print("Arduino is communicating")
                    return
            except:
                if self.verbose: print("Exception") # default print("Exception")
                exception_count = exception_count + 1 # If the try block experiences an exception, increment the exception count
            attempts = attempts + 1         # Increment the attempt count
            if 5 == attempts:
                print("Unable to communicate with Arduino...%d exceptions" % (exception_count))
                exit
    def send(self,str):                     # When called, this method writes data to he serial port encoded as a string
        #self.device.write("%s\n" % (str))   # Send the data with a linebreak character as an end-byte
        str = str + '\n' #added to include linebreak in encoded string
        self.device.write(str.encode())   # Send the data with a linebreak character as an end-byte
        if self.verbose: print("Sent '%s'" % (str))
    def getResp(self):                      # When called, it will continuially check the
        while True:
            if self.verbose: print("Waiting for response...")
            #str = self.device.readline()    # reads any characters in the serial line into the str variable, until a newline character is encountered
            str = self.device.readline().decode().split('\r\n')[0]    # reads any characters in the serial line into the str variable, until a newline character is encountered
            #str = str.replace("\n","")      # Replace newline characters with spaces
            #str = str.replace("\r","")      # Replace carriage return characters with spaces
            print("Got response: '%s'" % (str)) # Leaving this on all the time ensures that the console will scroll
            if str[:6] != "DEBUG:": return str # If Arduino debug is not active, return the str string variable
    def closePort(self):
        self.device.close()
        print("Port is now closed")
            
            
# ==============================================================================
# These functions exist outside of the scope of the above class definition, and are called
#                   within the geiger() function
# ==============================================================================
            
###===== setPeriod() function changes the Arduino's period variable via the void getPeriod(void) Arduino function ###
def setPeriod(c,period):
    command = "%d"%(1000*period)    # Encodes period into string, and converts from seconds to milliseconds
    c.send("%s\n"%command)          # Send period with a new line character as and byte
    resp = c.getResp()              # Get response to check it was received well
    if resp != command:             # let user know of a problem, close the port to avoid having to restart the kernel, then raise an exception
        print(("Seek attention: response to '%s' was '%s'"%(command,resp))) 
        c.close()
        raise ValueError
    c.getResp()  # Clears serial using self.device.readline() function
    c.getResp()


###===== When this is called, the script will start calling relevant functions ###
def geiger(replicas=2, intervals=10, period=0.2,graphics=True):
    saveFileName=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") +"_period"+str(period)+"_int"+str(intervals)+"_rep"+str(replicas)+ "_COUNTING_DATApy3.csv"
    print("Connecting to Arduino\n")
    a = GeigerArduino()                 # Initialize instance of the GeigerArduino class
    print("\nSetting period\n")
    setPeriod(a,period)                 # Set period variable onboard the Arduino depending on user input
    print("\nStarting data collection\n")
                                       # Sets starting maximum of the x-axis, will get updated later in the nested for-loops
    heights = numpy.zeros((replicas,intervals),dtype=int)  # Init 2D array with replicas number of rows, and max_events+1 number of columns
       
    # Data Acquisition and Plotting
    for i in range(replicas):                    # This for-loop will restart graphing after interval count has been reached
        for k in range(intervals):               # This for-loop will acquire the counts of events per intervals of time, and will replot it in the console
            
            j = int(a.getResp())                # Get count from last period, cast to an integer type just in case
          
            heights[i, k]=j
            
    for i in range(replicas): # Histogram graphing section, to visually check if the data is decent. 
       p.hist(heights[i,:],)
       p.title("Replica #%d" % (i+1)) # Only the last plot is visible 
       #i+=1 # This is not necessary
            
    #if saveFileName and len(saveFileName) > 0:  # If the variable saveFileName is defined and has a length greater than 0 # this doesn't work to check if variable is defined, throws NameError, should use try statement
    try:
        print('Mean Count', numpy.mean(heights))
        numpy.savetxt(saveFileName,heights, delimiter=",")     # Save file
        print("data saved to disk as '%s'." % (saveFileName))
        a.closePort()
    except:
        a.closePort()
    return heights

# ==============================================================================
#                               Run the script!
# ==============================================================================
    
#rc = geiger(replicas=1,   intervals=100,period=0.2,graphics=False)
rc = geiger(replicas=1,   intervals=10,period=0.2,graphics=False)
