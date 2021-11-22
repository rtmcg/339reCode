# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018

@author: James Fraser

And Greg 2020-21

"""
import tkinter as tk
import GraphingClass_python3_edit4 as gc # change if filename changes
#import sys
import threading
class Interface:
###### WIDGET INITIALIZATION FUNCTIONS ################################################################################################################################################################################################
    def __init__(self, frame, obj, verbose = 0):
        
        ## Frame and argument 
        self.frame = frame                          # Associate tkinter object, tk.Tk() in PythonController
        self.obj = obj                              # Associate Serial object
        self.frame.attributes("-topmost", True)     # Keep on top
        self.frame.title("Arduino GUI Controller")  
        self.verbose = verbose 
        if self.verbose : print("\nTKINTERCLASS, VERBOSE MODE ACTIVATED")
        
        ## Storage arry initialization, permit arbitrary number of variables and also permits configurability when widgets are made via for loops
        self.recButtArry=[]         # An arry of the various buttons, to allow access to them from outside this method
        self.recEntryArry=[]        # Stores entries, allowing getter and setters to access their fields
        self.initVarButts = []      # Arry to store them and access them later  
        self.initVarEntry = []      # Array for variable entries
        self.startedFlag = 0        # Used for start button

        rowCount = 0                # Used for entry rows
        
        ## Create Labels for each init variable, can grow arbitrarily large
        # the buttons are placed into an array, making them accesible in other methods and also outside of the initialized createInterface class
        for i in self.obj.initVar: 
            name = i[1]+ " (" +i[3] +"): "
            startingVal = i[2]
            row = rowCount
            label = tk.Label(self.frame, text=name)
            label.grid(column=0,row= row)
            band = tk.Entry(self.frame)
            startingVal = str(round(float(startingVal),3))  # Round the float for aesthetic reasons
            band.insert(0, startingVal)
            band.config(justify=tk.CENTER)
            self.initVarEntry.append(band)            
            self.initVarEntry[rowCount].grid(column = 1, row = rowCount) # makes grid of entries
            sett = tk.Button(self.frame, text = "SET", width = 10, command = lambda row = row: self.setButtonCMD(row)) # Have to reassign the row variable within lambda, in order to avoid scope issue where all buttons passed arg equal to the final assignment of row
            sett.configure(state = 'disabled') # Disabled by default to avoid data loss when START is pressed and the record of SET changes is overwritten.
            self.initVarButts.append(sett) # appends set button
            self.initVarButts[row].grid(column = 2, row = row) # create grid out of buttons
            rowCount += 1  # increment row
            
        ## Create Savefile zone
        self.saveLabel = tk.Label(self.frame, text="Save Filename: ") # create save label
        self.saveLabel.grid(column = 0, row = rowCount, pady = (15,2)) # create save label in grid, with y padded
        self.saveEntry = tk.Entry(self.frame) # create save entry in frame
        self.saveEntry.grid(column = 1, row = rowCount, pady = (15,2)) # place save entry in grid
        self.saveButt = tk.Button(self.frame, text = "SAVE", width = 10,  command = self.saveButtonCMD, state='disabled') # create save button in frame, run savebuttoncmd when pressing
        self.saveButt.grid(column = 2, row = rowCount, pady = (15,2)) # place save button in grid
       
        rowCount += 1
         
        ## Create START, STOP, and QUIT buttons
        self.endButt = tk.Button(self.frame, text = "QUIT", width = 10, command = self.exitButtonCMD )
        self.endButt.grid(column = 0, row = rowCount, pady = 10)  
        self.stopButt = tk.Button(self.frame, text = "PAUSE", width = 10, command = self.pauseButtonCMD, state='disabled' )
        self.stopButt.grid(column = 1, row = rowCount, pady = 10)   
        self.startButt = tk.Button(self.frame, text = "START", width = 10, command = self.startButtonCMD )
        self.startButt.grid(column = 2, row = rowCount, pady = 10) 
        
        rowCount += 1
        
        ## Magic numbers for formatting for the main page, only really used once, but good to have if anything is added later
        mainWindowWidth = 580
        mainWindowHeight = (20*rowCount+150)
        
        note = tk.Label(self.frame, text = "Leave filename field empty for a timestamp default. \nThe filetype '.csv' will be appended automatically to your input.\n\nPressing PAUSE and then START will wipe any recorded data,\nso it is highly recommended that you SAVE your data."
                        ,justify = tk.CENTER, width = 80) # create note label
        note.grid(column = 0, row = rowCount, columnspan = 3, pady = (0,10)) # place not in grid
        rowCount += 1 # increase row count

        self.frame.geometry("%dx%d%+d%+d" % (mainWindowWidth, mainWindowHeight, 400, 400)) # create geometry of the main window
        self.frame.resizable(width=False, height = True) # make height resizable 
        
        self.frame.protocol("WM_DELETE_WINDOW", self.buttonOverride)     # Overrides the big red X button, limiting user choice and avoiding an unclean exit

        ## Init data storage for copy from ArduinoClass and then graphing
        self.getMainStorage()
        
        ## Start thread for parallel script execution # changed for python 3, just run mainloop in python controller
        # Removed for python 3
    
###### MAIN WINDOW BUTTON HANDLER METHODS ################################################################################################################################################################################################
 
    
    def startButtonCMD(self):     
        print("\nSTARTING")
        self.stopButt.configure(state = 'active') # change active states of buttons
        self.saveButt.configure(state = 'disabled')
        self.startButt.configure(state = 'disabled')
        self.obj.mainStorage = [] # used for values from arduino
        self.obj.initSetRecord = [] # list for initial settings
        
        if self.startedFlag != 1: # if not started
            self.obj.start()    # Change data collection variable in the serial object  
            self.recZones()     # Create window for showing off the recorded values
            self.setRecValues() # Start re-occuring function that auto updates the values in the entry fields
            self.startedFlag = 1
            
        for i in self.initVarButts: # Enable the SET values 
            i.configure(state='active') # makes buttons active
            
        self.obj.send("START") # send to arduino, case 5 in parsecommand
        self.obj.running = True # sets arduino class for temp to running
                        
    def exitButtonCMD(self):
        print("\nEXITING")
        
        if self.verbose: print("\nStopping data collection")
        self.obj.stop() # runs stop method, sends stop to arduino
        
        if self.verbose: print("\nClosing port")
        self.obj.closePort() # closes serial port
        
        if self.verbose: print("\nClosing GUI window")
        self.frame.quit() # quits tkinter frame
        
        if self.verbose: print("\nDeleting GUI object")
        self.frame.destroy() # destroys tkinter frame
        self.obj.thread.join()
        print("Thread alive:", self.obj.thread.is_alive())
      
        print("\nSuccessful exit, you can now safely restart the app.\n")        
       
    def setButtonCMD(self, yeet):
        print("\n\nSETTING")
        entryObj = self.initVarEntry[yeet]  # Get reference to appropriate Entry object
        value = entryObj.get()              # Retrieve the string value
        name = self.obj.initVar[yeet, 1]    # This is a matrix, and we only want the second column of string variables        
        self.obj.set(name, value)   # now that those values are extracted, call the set function with the values as arguments

    def saveButtonCMD(self):
        print("\nSAVING")    
        saveFileName = self.saveEntry.get() # gets the entry for filename
        self.obj.save(saveFileName) # saves file
        self.saveEntry.delete(0, 'end') # deletes all characters in save entry

    def pauseButtonCMD(self):
        print("\nPAUSING")
        self.obj.stop() # sends stop to arduino
        self.saveButt.configure(state = 'active') # change button to active
        self.startButt.configure(state = 'active')        
        for i in self.initVarButts: # Disable the SET buttons to avoid data loss when START is pressed and the record of SET changes are overwritten  
            i.configure(state = 'disabled') 
            
##### REC WINDOW METHODS ######################################################################
       
        
    def recZones(self):
        print("Creating window to display recorded data. Recorded variables are:")   # Start UI window for data display   
        print(self.obj.headerTable, "\n") # prints headers, variable names
        row = 0        
        self.dataRec = tk.Toplevel(self.frame) # top level window on frame
        self.dataRec.geometry("%dx%d%+d%+d" % (300, 110*len(self.obj.headerTable), 0, 0)) # sets appearance of top level window
        
        for i in self.obj.headerTable:        # Iterate through all the RECORD variables, creating zones for them
            if i != 'Time Index': # if not this, not needed to watch
                label = tk.Label(self.dataRec, text=i) # create label with text of variable
                label.pack() # put together widgets
                entry = tk.Entry(self.dataRec) # create entry on datarec window
                entry.config(justify=tk.CENTER) # center entry
                self.recEntryArry.append(entry) # add to record entry array
                self.recEntryArry[row].pack() # put entries into window
                button = tk.Button(self.dataRec, text = "PLOT", width = 10,  command = lambda row = row: self.plotButtonCMD(row)) # Row var re-assigned due to scoping issue, as stated during init section
                self.recButtArry.append(button)                           # Use this to access the buttons later for unique congifuration
                self.recButtArry[row].pack(pady = 10) # place buttons
                row += 1        
                
        message = tk.Message(self.dataRec, text = "Precision of measurements truncated for display. Only showing every 1-in-10 data points or so of the total being recorded to memory.\n\nWindow will close when application is quit."
                             , width = 250, justify = tk.CENTER)
        message.pack() # add message to window
        self.dataRec.protocol("WM_DELETE_WINDOW", self.buttonOverride) # Replaces functionality of the big red X button in the top right
        self.dataRec.resizable(width=False, height = True) # Can't change the size of it
        self.dataRec.title("\n\nRecorded Variables")
        self.dataRec.attributes("-topmost", True)   # Keep it at the top of all o
        
    def plotButtonCMD(self, row):      
        win = tk.Toplevel(self.frame) # create top level window
        message = "Graphing every 10 measurements of: " + str(self.obj.headerTable[row]) # message with variable
        graph = gc.Graph(win, self.obj, row, verbose = self.verbose) # creates graph from graphingclass      
        tk.Label(win, text=message).pack() # message label
        tk.Button(win,text = 'CLOSE', command = lambda graph = graph, win = win: self.plotCloseButtonCMD(graph, win)).pack() # button for closing graph
        win.protocol("WM_DELETE_WINDOW", self.buttonOverride)  # Overrides the big red X button, limiting user choice and avoiding an unclean exit
        win.resizable(width = False, height = False)  # makes window resizable
        win.title("\n LIVE GRAPH") # title of window
        win.attributes("-topmost", True)  # keeps window on top
        win.geometry("%dx%d%+d%+d" % (600, 600, 400, 400))
        for i in self.recButtArry:
            i.config(state = "disabled")    # to prevent user from opening a bajillion windows and freezing the program
        
          
    def setRecValues(self): # Updates the values displayed on the recorded variables window
        if self.obj.running:
             try:   
                index = 0
                if len(self.allData) > 0: # if data from arduino
                    for i in self.recEntryArry:       # Access the ith element of the latest array in allData
                        data = self.allData[-1] # get the last data
                        i.delete(0, tk.END) # delete value in entry
                        i.insert(0, "%.4f" % data[index]) # insert new data
                        index += 1
             except:
                 print("Unable to show recorded values, is the window closed and are there values to update with?")
     
        self.frame.after(1000, self.setRecValues)     # Will re-call this function every second



        
###### GRAPHING WINDOW METHODS ################################################################################################################################################################################################
    
    
    def plotCloseButtonCMD(self, graph, win):
        del graph # deletes graphingclass object
        win.destroy() # destroys window
        del win # deletes window object
        for i in self.recButtArry: # sets buttons to active
            i.config(state = "active")
    

###### OTHER METHODS ################################################################################################################################################################################################


    def getMainStorage(self):
        self.allData = self.obj.mainStorage             # copies the data from the arduino
        self.frame.after(1000, self.getMainStorage)     # Will re-call this function every second
    
    def buttonOverride(self): # for red X button override
        print("Button disabled.")

