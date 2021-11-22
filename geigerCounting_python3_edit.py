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

class GeigerArduino: # class for the arduino, send and receive data and close
    def __init__(self, verbose = 0):   # Verbose mode will let give you a lot more information, and is best used in conjunction with debug==2 in Arduino, default = 0
        self.verbose = verbose      # Sets the instance attribute equal to the user's input or the default value
        #if verbose: print("introArduino class creator: Verbose mode activated")
        if verbose: print("GeigerArduino class creator: Verbose mode activated") # not sure where "intro" came from
        #for i in range(2,10):       # Iterate through a series of port options, trying to see if the Arduino is connected # better they assign the com port themselves
            #device = "COM%d" % (i)  # Encode current port option
        device = "COM4" # Encode current port option
        #if verbose: print(("Trying '%s'"%(device)))
        if verbose: print(f"Trying '{device}'") # if verbose, print trying with device number
        try:                    # If there is an exception when the serial.Serial() method is called, the script won't crash, and instead will try other things
            self.device = serial.Serial(device, baudrate = 9600, timeout = 2.0)  # Initialize an isntance of PySerial's serial connection, with the variable name self.device (in this case it'll be a.handle())
            #if verbose: print("Found device at %s" % (device)) # print device if verbose
            if verbose: print(f"Found device at {device}") # print device if verbose
            #break
        except:                     # Code within this will execute right after an exception happens in the try part
            print('Device not found') # print if not found
            #continue
        buf = self.device.read(10000)   # Clean out the buffer by reading bytes
        #if self.verbose: print(("cleared %d bytes"%(len(buf))))
        if self.verbose: print(f"cleared {len(buf)} bytes") # print the amount of bytes cleared
        #self.device.setDTR(1);          # Reboot Arduino # DTR is what resets the arduino
        #self.device.setDTR(0);          # DTR is a holdover from old-school serial communications. Stands for Data Terminal Ready
        #self.device.setDTR(1);
        self.device.setDTR(1)          # Reboot Arduino # DTR is what resets the arduino
        self.device.setDTR(0)          # DTR is a holdover from old-school serial communications. Stands for Data Terminal Ready
        self.device.setDTR(1) # ; are not needed
        exception_count = 0             # Init an exception counter
        attempts = 0                    #  Init an attempt counter
        while True:                     # Infinite loop, is controlled by the previous two counters
            try: # try unless exception
                if "HELLO" == self.getResp(): # Calls the getResp() method, which performs a readline(). This is the Python trying to handshake with Arduino
                    if verbose: print("Arduino is communicating") # print if verbose
                    return # return nothing
            except: # run if try doesn't work
                if self.verbose: print("Exception") # default print("Exception")
                #exception_count = exception_count + 1 # If the try block experiences an exception, increment the exception count
                exception_count += 1 # If the try block experiences an exception, increment the exception count
            #attempts = attempts + 1         # Increment the attempt count
            attempts += 1         # Increment the attempt count
            if 5 == attempts: # if 5 attempts have occurred
                #print("Unable to communicate with Arduino...%d exceptions" % (exception_count))
                print(f"Unable to communicate with Arduino...{exception_count} exceptions") # print exception count
                #exit # exit program
                exit() # exit program
    def send(self, strr):                     # When called, this method writes data to he serial port encoded as a string, changed to strr since str is a python keyword
        #self.device.write("%s\n" % (str))   # Send the data with a linebreak character as an end-byte
        strr = strr + '\n' #added to include linebreak in encoded string
        self.device.write(strr.encode())   # Send the data with a linebreak character as an end-byte
        #if self.verbose: print("Sent '%s'" % (strr))
        if self.verbose: print(f"Sent '{strr}'") # if verbose, show what was sent
    def getResp(self):                      # When called, it will continuially check the serial port
        while True:                         # run while something is in loop
            if self.verbose: print("Waiting for response...") # print if verbose
            #str = self.device.readline()    # reads any characters in the serial line into the str variable, until a newline character is encountered
            strr = self.device.readline().decode().split('\r\n')[0]    # reads any characters in the serial line into the str variable, until a newline character is encountered
            #str = str.replace("\n","")      # Replace newline characters with spaces
            #str = str.replace("\r","")      # Replace carriage return characters with spaces
            #print("Got response: '%s'" % (strr)) # Leaving this on all the time ensures that the console will scroll
            print(f"Got response: '{strr}'") # Leaving this on all the time ensures that the console will scroll
            if strr[:6] != "DEBUG:": return strr # If Arduino debug is not active, return the str string variable
    def closePort(self): # close port function
        self.device.close() # closes port
        print("Port is now closed") # prints out
            
            
# ==============================================================================
# These functions exist outside of the scope of the above class definition, and are called
#                   within the geiger() function
# ==============================================================================
            
###===== setPeriod() function changes the Arduino's period variable via the void getPeriod(void) Arduino function ###
def setPeriod(c, period): # function used to set period
    #command = "%d"%(1000*period)    # Encodes period into string, and converts from seconds to milliseconds
    command = f"{1000*period}"    # Encodes period into string, and converts from seconds to milliseconds
    #c.send("%s\n"%command)          # Send period with a new line character as and byte
    c.send(f"{command}\n")          # Send period with a new line character as and byte
    resp = c.getResp()              # Get response to check it was received well
    if resp != command:             # let user know of a problem, close the port to avoid having to restart the kernel, then raise an exception
        #print(("Seek attention: response to '%s' was '%s'"%(command,resp))) 
        print(f"Seek attention: response to '{command}' was '{resp}'") # prints period and response to it
        c.close() # close if response is equal to command
        raise ValueError # raise error to notify user
    c.getResp()  # Clears serial using self.device.readline() function
    c.getResp()


###===== When this is called, the script will start calling relevant functions ###
def geiger(replicas = 2, intervals = 10, period = 0.2): # used to run class and functions
    saveFileName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_period" + str(period) + "_int" + str(intervals) + "_rep" + str(replicas) + "_COUNTING_DATApy3.csv" # save file name setup
    print("Connecting to Arduino\n") # printed out
    a = GeigerArduino()                 # Initialize instance of the GeigerArduino class
    print("\nSetting period\n") # printed out
    setPeriod(a, period)                 # Set period variable onboard the Arduino depending on user input
    print("\nStarting data collection\n") # printed out
                                       # Sets starting maximum of the x-axis, will get updated later in the nested for-loops
    heights = numpy.zeros((replicas, intervals), dtype = int)  # Init 2D array with replicas number of rows, and max_events+1 number of columns
       
    # Data Acquisition and Plotting
    for i in range(replicas):                    # This for-loop will restart graphing after interval count has been reached
        for k in range(intervals):               # This for-loop will acquire the counts of events per intervals of time, and will replot it in the console
            
            j = int(a.getResp())                # Get count from last period, cast to an integer type just in case
          
            heights[i, k] = j # filling up heights array with reads from serial port
            
    for i in range(replicas): # Histogram graphing section, to visually check if the data is decent. 
       p.hist(heights[i,:],) # plot histogram for each replica
       p.title("Replica #%d" % (i+1)) # Only the last plot is visible 
       #i+=1 # This is not necessary
            
    #if saveFileName and len(saveFileName) > 0:  # If the variable saveFileName is defined and has a length greater than 0 # this doesn't work to check if variable is defined, throws NameError, should use try statement
    try: # try to save and print mean and filename
        print('Mean Count', numpy.mean(heights)) # print mean of heights
        numpy.savetxt(saveFileName,heights, delimiter=",")     # Save file
        #print("data saved to disk as '%s'." % (saveFileName)) # print data saved to filename
        print(f"data saved to disk as '{saveFileName}'.") # print data saved to filename
        a.closePort() # close the port
    except: # run if try gives an exception
        a.closePort() # close the port
    return heights # return heights from function

# ==============================================================================
#                               Run the script!
# ==============================================================================

rc = geiger(replicas = 1, intervals = 100, period = 0.2) # Before there was a 'graphics' parameter, but that didn't do anything. Run geiger function
