# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018

@author: James Fraser

"""

import serial
import numpy as np
import datetime
import struct
import threading

class Arduino:
    def __init__(self,verbose=1):
        
        self.verbose = verbose
        self.running = False  
    
        self.mainStorage = []
        self.headerTable = []
        self.unitTable = []
        self.initVar =[] 
        self.initSetRecord = []
        
        self.initVarCount = 0
        self.recVarCount = 0

        if self.verbose: print("ARDUINO, VERBOSE MODE ACTIVATED\n")        
        print("\n\nInitializing serial object\n")
        
        connectAttempt = 0
        maxCount = 8
        for i in range(0,maxCount):
            device = "COM%d" % (i) 
            try:
                connectAttempt += 1
                self.device = serial.Serial(device,baudrate=115200,timeout=1.0) 
               # self.device.open()
                print("Found device at %s \n" % (device))
                break
            except:
                if (connectAttempt == maxCount):
                    raise Exception("Unable to connect to Arduino after %d attempts. Check that it's plugged in and the drivers are properly installed." % (connectAttempt - 1))
                continue   
        self.device.setDTR(1); #reboot Arduino
        self.device.setDTR(0);
        self.device.setDTR(1);
        exception_count = 0
        attempts = 0
        trying = True
        while trying:
            try:
                self.send("HANDSHAKE\n")
                resp = self.getResp()
                resp = resp.replace("\t","")
                if resp == "HANDSHAKE":
                    print("Successful handshake, Arduino and Python are communicating\n") 
                    trying = False
                    break
            except:
                if self.verbose: print("Exception")
                exception_count = exception_count + 1
            attempts = attempts + 1
            if self.verbose: print("\nattempts =", attempts)
            if 15 == attempts:
                trying = False
                self.device.close()
                raise Exception("\nUnable to handshake with Arduino...%d exceptions" % attempts)
                break  
            
            
        self.getInitVar()
        self.thread = threading.Thread(target = self.dataCollection, name = "Data collection loop") #each of these threads should loop infinitely
       
        

    ## Send a line of string to Arduino ##
    def send(self,strr):
        #self.device.write("%s\n" % (str)) #commented out for python3
        strr = strr + '\n' #added for python3
        self.device.write(strr.encode()) #changed for python 3
        if self.verbose: print("\nSent '%s'\n" % (strr))
   
     
    ## Read and slightly clean a line from Arduino ##
    def getResp(self):
        #str = self.device.readline() #commented out for python3

        strr = self.device.readline().decode('ISO-8859-1').split('\r\n')[0].replace('\n', '') #changed for python3 #added 'ISO-8859-2' or 'ISO-8859-1'

        #str = str.replace("\n","") #commented out for python3
        #str = str.replace("\r","") #commented out for python3
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
                        if (i is not'=' )and (i != ""): # cleans junk
                            outputArry.append(i)    # Put into the variable array
            elif (rawVar == "READY"):               # Indicates all INIT variables have been sent
                trying = False                      # Change run condition
                print("\nINIT variables acquired: ")
                outputArry = np.reshape(outputArry, (rowCount-1,4))     # Minus 1 because there's a junk line to remove
                for i in outputArry:
                    i[2] = self.convertHexToDec(i[2])                   # Convert the values from hex float to dec float
                print(outputArry)   
                self.initVar = outputArry
                self.initVarCount = rowCount-1            
    
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
                self.headerTable.append('Time Index')  
                self.recVarCount = len(self.headerTable)
                
    ## Get access to the TKInter object's methods, since it was initialized after this Arduino class ##                                   
    def associate(self, frame): 
        self.frame = frame        
        
    ## Start the program. This is called only once, and from the tkinter object.
    def start(self):       
        self.mainStorage = []
        print("\nBeginning data acquisition, this may take a moment or two, depending on certain settings\n")       
        clearing = True     
        attemptCount = 0
        while clearing :    # This while loop clears the junk, and will permit the START signal to be properly received. could probably be optimized
            if attemptCount == 5:
                raise Exception("EXCEPTION: Unable to successfully start data acquisition.")
            #resp = self.device.readline()   # Clears junk
            resp = self.device.readline().decode(errors='ignore')#.split('\r\n')[0]   # Clears junk #changed for python3
            if self.verbose : print("Response in start method:", resp)
            if (resp ==''):                 # THIS DOES NOT SEEM LIKE A GOOD SOLUTION              
                attemptCount +=1              
                self.send("START")
                #resp = self.device.readline()
                resp = self.device.readline().decode(errors='ignore')#.split('\r\n')[0]  #changed for python3
                if (resp == 'INDEX\t0\t1\n'):    
                    clearing = False
                    if self.verbose: print("Done clearing junk!")
            elif (resp =='INDEX\t0\t1\n'):
                clearing = False
                if self.verbose: print("Done clearing junk!")
                
        self.genLabelTables()               # Get string table of labels from Arduino, should grow arbitrarily large. 
                                            # If start() = self.send("START"), would need to put the clearing code into  self.genLabelTables()

    ## Stops data collection and data retention
    def stop(self):   
        self.send("STOP")
        self.running = False
        
    ## Function to change parameters defined on the Arduino. Best used only when running, and could probably use a run condition based on the flag self.running
    def set(self, varName, inputVal): 
        try:
            inputVal = str(float(inputVal))
        except:
            print("\nCANNOT SET, BAD INPUT: Only integer and float values are accepted.\n")
            return
        apple = 1
        
        if self.running == True : 
            if self.verbose: print("PAUSING")
            self.running = False
            #self.stop()
            apple = 0       # flag to let the later code know we've temporarily turned off the running condition
            
        print("Sending to Arduino")                                                  
        packedMessage = "SET "+ varName + " " + str(inputVal) 
        if len(self.mainStorage) > 0 :
            latestVals = self.mainStorage[-1]
        else:
            latestVals = [0]
        self.initSetRecord.append([varName, inputVal, latestVals[0]])
        
        self.send(packedMessage)
        self.device.flush() # Wait for the serial line to finish clearing
        self.send("\n")     # Add a newline character to finish the message
        
        print("Sent " +packedMessage+ " to Arduino")                   
                               
        if apple == 0:    # If the flag has been set to 0, restart the reading of data      
            self.running = True

    ## Saves the data from main storage, and if there are any SET operations done, that also will be stored
    def save(self, saveFileName):   
        
        ## Handle the filename
        if saveFileName == '':
            timeDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            saveFileName =  timeDate + " PRIMARY THERMAL DATA.csv"    
            initRecName =  timeDate + " INIT CHANGES.csv"  
        elif saveFileName != '':
            initRecName = saveFileName + " INIT CHANGES.csv"
            saveFileName = saveFileName + '.csv'
            
        ## Add the header table to the main storage array, for ease of reading when the data is examined later
        self.mainStorage.insert(0,self.headerTable) 
        if self.verbose: print("Main storage array:", self.mainStorage)
        
        ## Actually Save      
        np.savetxt(saveFileName, self.mainStorage, delimiter =",", fmt = '%s')
        print("\n\nSaved main storage under the filename: ", saveFileName, "\n\n")
        
        ## If there's any SET operations recorded, save them too
        if len(self.initSetRecord) > 0:
            initRecHeader =["Variable", "Value", "Time Index"]
            self.initSetRecord.insert(0, initRecHeader)
            np.savetxt(initRecName, self.initSetRecord, delimiter = ',' , fmt = '%s')
            print("Changes to INIT variables have been recorded and saved as: ", (initRecName))
            
   ## Convenient to have a function to close the serial port 
    def closePort(self):      
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
                resp = self.getResp()               # Readline
                if resp != '':                      # Necessary, because had to add a Serial.println() in Arduino that limits problems junk data
                    respSplit = resp.split("\t")    # Create table
                    
                    if (len(respSplit) != 5 ) and  (len(respSplit) != 3 ):  # Helps avoid processing junk
                        if self.verbose: print("\n\nGARBAGE FOUND IN dataCollection (", respSplit,") BAD RESPONSE LENGTH.\n\n")
                        
                    elif respSplit[0] == "INDEX":               # Get the time index
                        tempStorage.append(int(respSplit[2]))   # Append the index to tempStorage
                        
                    elif respSplit[0] == "VALUE":                       # Collect the unit
                        respConv = self.convertHexToDec(respSplit[3])   # Converts from hex float to decimal float
                        tempStorage.append(respConv)                    # Convert then add value to the tempStorage  
                        
                    else :
                        if self.verbose: print("\n\nGARBAGE FOUND IN dataCollection: ", resp, "\n\n")        # Catches the garbage of length 5 and 3
                        
                    if (len(tempStorage) == (len(self.headerTable))) :  # Once a block has been completely read, it's time to append the data to the main storage array
                            self.mainStorage.append(tempStorage)        # Add temp to main array
                            if self.verbose: print("DATA STORED AS: ", tempStorage, "\n")
                            tempStorage = []
                   
 #======== CONVERSION METHODS FOR DATA TRANSFER=======================#
 
    def convertHexToDec(self, hexVal): # Used to convert data sent from Arduino
        try:
            if hexVal == '0':
                hexVal = "00000000"
            #value = struct.unpack('!f', hexVal.decode('hex'))[0]
            value = struct.unpack('!f', bytes.fromhex(hexVal))[0] #changed for python3
            return value    
        except:
            print("JUNK DATA: " + hexVal)

