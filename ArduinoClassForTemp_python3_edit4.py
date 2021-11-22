# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018

@author: James Fraser

And Greg 2020-21

"""

import serial
import numpy as np
import datetime
import struct
import threading

class Arduino:
    def __init__(self,verbose=0):
        self.verbose = verbose
        self.running = False # when not running
        self.thread_run = True
        
        self.mainStorage = [] # where data from arduino is stored
        self.headerTable = [] # where recorded variables are stored
        self.unitTable = [] # where units are stored
        self.initVar = [] # list for initalized variables
        self.initSetRecord = [] # list for recording initial settings
        
        self.initVarCount = 0 # counts initial variables
        self.recVarCount = 0 # recorded variable counts

        if self.verbose: print("ARDUINO, VERBOSE MODE ACTIVATED\n")        
        print("\n\nInitializing serial object\n")
        
        connectAttempt = 0
        maxCount = 8 # how many connect attmpts to try
        for i in range(0, maxCount):
            #device = "COM%d" % (i) 
            try:
                connectAttempt += 1
                self.device = serial.Serial(device, baudrate = 115200, timeout = 1.0) # serial port instance with baudrate and timeout
               # self.device.open()
                #print("Found device at %s \n" % (device))
                print(f"Found device at {device} \n")
                break # leave loop if device found
            except:
                if (connectAttempt == maxCount): # if hasn't connected after maxcount attempts
                    #raise Exception("Unable to connect to Arduino after %d attempts. Check that it's plugged in and the drivers are properly installed." % (connectAttempt - 1))
                    raise Exception(f"Unable to connect to Arduino after {(connectAttempt - 1)} attempts. Check that it's plugged in and the drivers are properly installed.")
                continue   
        #self.device.setDTR(1); #reboot Arduino
        #self.device.setDTR(0);
        #self.device.setDTR(1);
        self.device.setDTR(1) #reboot Arduino
        self.device.setDTR(0)
        self.device.setDTR(1)        
        exception_count = 0
        attempts = 0
        trying = True # keeps loop running
        while trying:
            try:
                self.send("HANDSHAKE\n") # send to arduino, which initializes and sends handshake back
                resp = self.getResp() # readline from arduino
                resp = resp.replace("\t","") # get rid of tabs
                if resp == "HANDSHAKE": # if get this from arduino
                    print("Successful handshake, Arduino and Python are communicating\n") 
                    trying = False # stop sending and looking for handshake
                    break # leave loop
            except: # if no handshake
                if self.verbose: print("Exception") 
                #exception_count = exception_count + 1
                exception_count += 1
            #attempts = attempts + 1
            attempts += 1
            if self.verbose: print("\nattempts =", attempts)
            if 15 == attempts: # after 15 attempts
                trying = False # stop trying
                self.device.close() # close port, print exception and leave loop
                #raise Exception("\nUnable to handshake with Arduino...%d exceptions" % attempts)
                raise Exception(f"\nUnable to handshake with Arduino...{attempts} exceptions")
                break  
                   
        self.getInitVar() # run function to get initial variables
        self.thread = threading.Thread(target = self.dataCollection, name = "Data collection loop") # each of these threads should loop infinitely # just data collection thread now, creates thread that is started in pythoncontroller
        

    ## Send a line of string to Arduino ##
    def send(self,strr):
        strr = strr + '\n' #added for python3
        self.device.write(strr.encode()) #changed for python 3
        if self.verbose: print("\nSent '%s'\n" % (strr))
   
     
    ## Read and slightly clean a line from Arduino ##
    def getResp(self):
        strr = self.device.readline().decode('ISO-8859-1', errors='ignore').split('\r\n')[0].replace('\n', '') #changed for python 3
        if self.verbose: print("Raw resp: '%s' " % (strr))
        return strr
    
        
    ## Function for acquiring INIT variables defined in the Arduino code, necessary to start the main window ##
    def getInitVar(self) :
        if self.verbose : print("\nAcquiring INIT variables from Arduino\n")
        rowCount = 0
        outputArry = []
        trying = True     # Run condition
        while trying:
            rawVar = self.getResp()                 # Get it    
            if (rawVar != "READY") :                # After HANDSHAKE is sent, ARduino responds with all the INIT variables, followed by READY
                    splitVar = rawVar.split("\t")   # Clean it
                    rowCount+=1                     # Add to count
                    for i in splitVar:
                        #if (i is not'=' )and (i != ""): # cleans junk
                        if i != '=' and i != "": # cleans junk # is not gave a warning, said to use !=
                            outputArry.append(i)    # Put into the variable array
                
            elif (rawVar == "READY"):               # Indicates all INIT variables have been sent
                trying = False                      # Change run condition
                print("\nINIT variables acquired: ")
                outputArry = np.reshape(outputArry, (rowCount-1,4))     # Minus 1 because there's a junk line to remove
                for i in outputArry:
                    i[2] = self.convertHexToDec(i[2])                   # Convert the values from hex float to dec float
                print(outputArry)   
                self.initVar = outputArry # initial variables set to output array
                self.initVarCount = rowCount-1 # counts initial variables            
    
    ## Using the first two batches of data from the Arduino, two tables for the  ##
    # This is not used for the INIT variables.
    def genLabelTables(self):
        run = 0                                  # Running condition for the while loop
        if self.verbose: print("CREATING LABEL TABLES")
        while run == 0:
            line = self.getResp()                # Read line of data
            line = line.split("\t")              # Split data by tab 
            print("\nLINE: ", line)
            if (line[0] =="VALUE"):              # Lines with VALUE in the first position represent the recorded variables
                self.headerTable.append(line[1]) # Index one is where the variable names are stored
                self.unitTable.append(line[4])   # Index four is where the variale's units are stored
                if self.verbose : print("Header Table: ", self.headerTable)
                if self.verbose : print("Unit Table: ", self.unitTable)
            elif (line[0] == "INDEX"):           # If it begins with INDEX, then one full block has been completed
                run = 1 
                self.headerTable.append('Time Index')   # add to header table
                self.recVarCount = len(self.headerTable) # number of variables received
                
    ## Get access to the TKInter object's methods, since it was initialized after this Arduino class ##                                   
    def associate(self, frame): # used in pythoncontroller to associate with tkinter, but is never used here
        self.frame = frame # gets tkinter frame 
        
    ## Start the program. This is called only once, and from the tkinter object.
    def start(self):       
        self.mainStorage = [] # list for data
        print("\nBeginning data acquisition, this may take a moment or two, depending on certain settings\n")       
        clearing = True # while clearing junk
        attemptCount = 0
        while clearing :    # This while loop clears the junk, and will permit the START signal to be properly received. could probably be optimized
            if attemptCount == 5: # if doesn't clear junk after 5 tries, raise exception
                raise Exception("EXCEPTION: Unable to successfully start data acquisition.")
            resp = self.device.readline().decode(errors='ignore')   # Clears junk #changed for python3
            if self.verbose : print("Response in start method:", resp)
            #if (resp ==''):                 # THIS DOES NOT SEEM LIKE A GOOD SOLUTION     
            if resp == '':                 # THIS DOES NOT SEEM LIKE A GOOD SOLUTION 
                attemptCount += 1              
                self.send("START") # write to arduino
                #resp = self.device.readline()
                resp = self.device.readline().decode(errors='ignore')#.split('\r\n')[0]  #changed for python3
                #if (resp == 'INDEX\t0\t1\n'): 
                print('raw_resp' , resp) # testing
                if resp == 'INDEX\t0\t1\n': # excpected response  
                    clearing = False # leave loop
                    if self.verbose: print("Done clearing junk!")
            #elif (resp =='INDEX\t0\t1\n'):
            elif resp == 'INDEX\t0\t1\n': # expected response
                clearing = False # leave loop
                if self.verbose: print("Done clearing junk!")
                
        self.genLabelTables()               # Get string table of labels from Arduino, should grow arbitrarily large. 
                                            # If start() = self.send("START"), would need to put the clearing code into  self.genLabelTables()

    ## Stops data collection and data retention
    def stop(self):   
        self.send("STOP")
        self.running = False
        self.thread_run = False
        #self.thread.join() # Get bad data collection if joined here
        #print('Thread alive:' , self.thread.is_alive())


    ## Function to change parameters defined on the Arduino. Best used only when running, and could probably use a run condition based on the flag self.running
    def set(self, varName, inputVal): 
        try:
            inputVal = str(float(inputVal)) # to check proper data type entered
        except:
            print("\nCANNOT SET, BAD INPUT: Only integer and float values are accepted.\n")
            return # return from function is not a good datatype
        apple = 1
        
        if self.running == True : 
            if self.verbose: print("PAUSING")
            self.running = False # stops data collection
            #self.stop()
            apple = 0       # flag to let the later code know we've temporarily turned off the running condition
            
        print("Sending to Arduino")                                                  
        packedMessage = "SET "+ varName + " " + str(inputVal) # put together set message
        if len(self.mainStorage) > 0: # if data in mainstorage
            latestVals = self.mainStorage[-1] # last value in main storage
        else:
            latestVals = [0] # if no values in main storage, probably should be [0,0,0,0], though set buttons are deactivated when program starts, so there should be some data 
        self.initSetRecord.append([varName, inputVal, latestVals[4]]) # changed latestVals[0] to latestVals[4] so time index is recorded, not out, gets variable and new set value
        
        self.send(packedMessage) # sends set message to arduino
        self.device.flush() # Wait for the serial line to finish clearing
        self.send("\n")     # Add a newline character to finish the message
        
        print("Sent " + packedMessage + " to Arduino")                   
                               
        if apple == 0:    # If the flag has been set to 0, restart the reading of data      
            self.running = True

    ## Saves the data from main storage, and if there are any SET operations done, that also will be stored
    def save(self, saveFileName):   
        
        ## Handle the filename
        if saveFileName == '': # if no save file name
            timeDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # get datetime string
            saveFileName =  timeDate + " PRIMARY THERMAL DATA.csv" # create filename
            initRecName =  timeDate + " INIT CHANGES.csv"  # create init changes filename
        elif saveFileName != '': # if there is a save filename
            initRecName = saveFileName + " INIT CHANGES.csv" # add init changes to filename
            saveFileName = saveFileName + '.csv' # add .csv to filename
            
        ## Add the header table to the main storage array, for ease of reading when the data is examined later
        self.mainStorage.insert(0, self.headerTable) 
        if self.verbose: print("Main storage array:", self.mainStorage)
        
        ## Actually Save      
        np.savetxt(saveFileName, self.mainStorage, delimiter =",", fmt = '%s')
        print("\n\nSaved main storage under the filename: ", saveFileName, "\n\n")
        
        ## If there's any SET operations recorded, save them too
        if len(self.initSetRecord) > 0:
            initRecHeader =["Variable", "Value", "Time Index"]
            self.initSetRecord.insert(0, initRecHeader) # put header at top of record
            np.savetxt(initRecName, self.initSetRecord, delimiter = ',' , fmt = '%s')
            print("Changes to INIT variables have been recorded and saved as: ", (initRecName))
            
   ## Convenient to have a function to close the serial port 
    def closePort(self):
        self.device.cancel_read() # added, was getting errors when closing
        self.device.close()
        del self.device
        if self.verbose: print("\nPort sould be closed now.\n")

        
#======== PRIMARY METHOD FOR DATA COLLECTION=======================#
## This is an inifinite loop continually running in a 'threading' thread. See documentation for info on threads.
# self.running is the flag by which is it activated and deactivated.
        
    def dataCollection(self):          ## Inf loop, started in a thread
        tempStorage = []
        
        if self.verbose : print("\nStarting data collection loop")
        
        while True:
            while self.running:    
                try:
                    resp = self.getResp()               # Readline
                except:
                    resp = '' # use continue to not return empty string when read errors, changed for python 3
                if resp != '':                      # Necessary, because had to add a Serial.println() in Arduino that limits problems junk data
                    respSplit = resp.split("\t")    # Create table
                    
                    #if (len(respSplit) != 5 ) and  (len(respSplit) != 3 ):  # Helps avoid processing junk
                    if len(respSplit) != 5 and len(respSplit) != 3:  # Helps avoid processing junk
                        if self.verbose: print("\n\nGARBAGE FOUND IN dataCollection (", respSplit,") BAD RESPONSE LENGTH.\n\n")
                        
                    elif respSplit[0] == "INDEX":               # Get the time index
                        tempStorage.append(int(respSplit[2]))   # Append the index to tempStorage
                        
                    elif respSplit[0] == "VALUE":                       # Collect the unit
                        respConv = self.convertHexToDec(respSplit[3])   # Converts from hex float to decimal float
                        tempStorage.append(respConv)                    # Convert then add value to the tempStorage  
                        
                    else :
                        if self.verbose: print("\n\nGARBAGE FOUND IN dataCollection: ", resp, "\n\n")        # Catches the garbage of length 5 and 3
                        
                    #if (len(tempStorage) == (len(self.headerTable))) :  # Once a block has been completely read, it's time to append the data to the main storage array
                    if len(tempStorage) == len(self.headerTable):  # Once a block has been completely read, it's time to append the data to the main storage array
                            self.mainStorage.append(tempStorage)        # Add temp to main array
                            if self.verbose: print("DATA STORED AS: ", tempStorage, "\n")
                            tempStorage = []
                
                   
 #======== CONVERSION METHODS FOR DATA TRANSFER=======================#
 
    def convertHexToDec(self, hexVal): # Used to convert data sent from Arduino
        try:
            if hexVal == '0':
                hexVal = "00000000"
            value = struct.unpack('!f', bytes.fromhex(hexVal))[0] #changed for python3
            return value    
        except:
            print("JUNK DATA: " + hexVal)

