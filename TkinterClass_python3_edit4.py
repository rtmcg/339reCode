# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018

@author: James Fraser

And Greg 2020-21

"""
import tkinter as tk
import GraphingClass_python3_edit4 as gc # change if filename changes


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
        self.initVarEntry = []
        self.startedFlag = 0

        rowCount = 0     
        
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
            
            self.initVarEntry[rowCount].grid(column=1, row = rowCount)
            sett = tk.Button(self.frame, text ="SET", width = 10, command = lambda row = row: self.setButtonCMD(row)) # Have to reassign the row variable within lambda, in order to avoid scope issue where all buttons passed arg equal to the final assignment of row
            sett.configure(state = 'disabled') # Disabled by default to avoid data loss when START is pressed and the record of SET changes is overwritten.
            self.initVarButts.append(sett)
            self.initVarButts[row].grid(column=2, row = row)
            rowCount+=1  
            
        ## Create Savefile zone
        self.saveLabel = tk.Label(self.frame, text="Save Filename: ")
        self.saveLabel.grid(column=0,row=rowCount, pady = (15,2))
        self.saveEntry = tk.Entry(self.frame)
        self.saveEntry.grid(column=1, row = rowCount, pady = (15,2))
        self.saveButt = tk.Button(self.frame, text = "SAVE", width = 10,  command = self.saveButtonCMD, state='disabled')
        self.saveButt.grid(column=2, row = rowCount, pady = (15,2))  
       
        rowCount+=1
         
        ## Create START, STOP, and QUIT buttons
        self.endButt = tk.Button(self.frame, text = "QUIT", width = 10, command = self.exitButtonCMD )
        self.endButt.grid(column=0, row=rowCount, pady=10)  
        self.stopButt = tk.Button(self.frame, text = "PAUSE", width = 10, command = self.pauseButtonCMD, state='disabled' )
        self.stopButt.grid(column=1, row=rowCount, pady=10)   
        self.startButt = tk.Button(self.frame, text = "START", width = 10, command = self.startButtonCMD )
        self.startButt.grid(column=2, row=rowCount, pady=10) 
        
        rowCount+=1
        
        ## Magic numbers for formatting for the main page, only really used once, but good to have if anything is added later
        mainWindowWidth = 580
        mainWindowHeight = (20*rowCount+150)
        
        note = tk.Label(self.frame, text = "Leave filename field empty for a timestamp default. \nThe filetype '.csv' will be appended automatically to your input.\n\nPressing PAUSE and then START will wipe any recorded data,\nso it is highly recommended that you SAVE your data."
                        ,justify = tk.CENTER, width = 80)
        note.grid(column=0, row = rowCount, columnspan = 3, pady=(0,10))
        rowCount+=1

        self.frame.geometry("%dx%d%+d%+d" % (mainWindowWidth, mainWindowHeight, 400, 400))
        self.frame.resizable(width=False, height = True) 
        
        self.frame.protocol("WM_DELETE_WINDOW", self.buttonOverride)     # Overrides the big red X button, limiting user choice and avoiding an unclean exit

        ## Init data storage for copy from ArduinoClass and then graphing
        self.getMainStorage()
        
        ## Start thread for parallel script execution # changed for python 3, just run mainloop in python controller
        
    
###### MAIN WINDOW BUTTON HANDLER METHODS ################################################################################################################################################################################################
 
    
    def startButtonCMD(self):     
        print("\nSTARTING")
        self.stopButt.configure(state='active')
        self.saveButt.configure(state='disabled')
        self.startButt.configure(state='disabled')
        self.obj.mainStorage = []
        self.obj.initSetRecord =[]
        
        if self.startedFlag != 1:
            self.obj.start()    # Change data collection variable in the serial object  
            self.recZones()     # Create window for showing off the recorded values
            self.setRecValues() # Start re-occuring function that auto updates the values in the entry fields
            self.startedFlag = 1
            
        for i in self.initVarButts: # Enable the SET values 
            i.configure(state='active')
            
        self.obj.send("START")
        self.obj.running = True
                        
    def exitButtonCMD(self):
        print("\nEXITING")
        
        if self.verbose: print("\nStopping data collection")
        self.obj.stop()
        
        if self.verbose: print("\nClosing port")
        self.obj.closePort()
        
        if self.verbose: print("\nClosing GUI window")
        self.frame.quit()
        
        if self.verbose: print("\nDeleting GUI object")
        self.frame.destroy()
        
        print("\nSuccessful exit, you can now safely restart the app.\n")        
       
    def setButtonCMD(self, yeet):
        print("\n\nSETTING")
        entryObj = self.initVarEntry[yeet]  # Get reference to appropriate Entry object
        value = entryObj.get()              # Retrieve the string value
        name = self.obj.initVar[yeet, 1]    # This is a matrix, and we only want the second column of string variables        
        self.obj.set(name, value)   # now that those values are extracted, call the set function with the values as arguments

    def saveButtonCMD(self):
        print("\nSAVING")    
        saveFileName = self.saveEntry.get()
        self.obj.save(saveFileName)
        self.saveEntry.delete(0,'end')

    def pauseButtonCMD(self):
        print("\nPAUSING")
        self.obj.stop()
        self.saveButt.configure(state='active')
        self.startButt.configure(state='active')        
        for i in self.initVarButts: # Disable the SET buttons to avoid data loss when START is pressed and the record of SET changes are overwritten  
            i.configure(state='disabled')
            
##### REC WINDOW METHODS ######################################################################
       
        
    def recZones(self):
        print("Creating window to display recorded data. Recorded variables are:")   # Start UI window for data display   
        print(self.obj.headerTable, "\n")
        row = 0        
        self.dataRec = tk.Toplevel(self.frame) 
        self.dataRec.geometry("%dx%d%+d%+d" % (300, 110*len(self.obj.headerTable), 0, 0))
        
        for i in self.obj.headerTable:        # Iterate through all the RECORD variables, creating zones for them
            if i != 'Time Index':
                label = tk.Label(self.dataRec, text=i)
                label.pack()
                entry = tk.Entry(self.dataRec)
                entry.config(justify=tk.CENTER)
                self.recEntryArry.append(entry)
                self.recEntryArry[row].pack()
                button = tk.Button(self.dataRec, text ="PLOT", width = 10,  command = lambda row = row: self.plotButtonCMD(row)) # Row var re-assigned due to scoping issue, as stated during init section
                self.recButtArry.append(button)                           # Use this to access the buttons later for unique congifuration
                self.recButtArry[row].pack(pady=10)
                row +=1        
                
        message = tk.Message(self.dataRec, text="Precision of measurements truncated for display. Only showing every 1-in-10 data points or so of the total being recorded to memory.\n\nWindow will close when application is quit."
                             , width = 250, justify = tk.CENTER)
        message.pack()
        self.dataRec.protocol("WM_DELETE_WINDOW", self.buttonOverride) # Replaces functionality of the big red X button in the top right
        self.dataRec.resizable(width=False, height = True) # Can't change the size of it
        self.dataRec.title("\n\nRecorded Variables")
        self.dataRec.attributes("-topmost", True)   # Keep it at the top of all o
        
    def plotButtonCMD(self, row):      
        win = tk.Toplevel(self.frame)   
        message = "Graphing every 10 measurements of: " + str(self.obj.headerTable[row])      
        graph = gc.Graph(win, self.obj, row, verbose = self.verbose)        
        tk.Label(win, text=message).pack()
        tk.Button(win,text='CLOSE', command = lambda graph = graph, win = win: self.plotCloseButtonCMD(graph, win)).pack()
        win.protocol("WM_DELETE_WINDOW", self.buttonOverride)     
        win.resizable(width=False,height=False) 
        win.title("\n LIVE GRAPH")
        win.attributes("-topmost", True)  
        win.geometry("%dx%d%+d%+d" % (600, 600, 400, 400))
        for i in self.recButtArry:
            i.config(state = "disabled")    # to prevent user from opening a bajillion windows and freezing the program
        
          
    def setRecValues(self): # Updates the values displayed on the recorded variables window
        if self.obj.running:
             try:   
                index = 0
                if len(self.allData) > 0:
                    for i in self.recEntryArry:       # Access the ith element of the latest array in allData
                        data = self.allData[-1]
                        i.delete(0, tk.END)
                        i.insert(0, "%.4f" % data[index])
                        index += 1
             except:
                 print("Unable to show recorded values, is the window closed and are there values to update with?")
        self.frame.after(1000, self.setRecValues)     # Will re-call this function every second


        
###### GRAPHING WINDOW METHODS ################################################################################################################################################################################################
    
    
    def plotCloseButtonCMD(self, graph, win):
        del graph
        win.destroy()
        del win
        for i in self.recButtArry:
            i.config(state = "active")
    

###### OTHER METHODS ################################################################################################################################################################################################


    def getMainStorage(self):
        self.allData = self.obj.mainStorage             # copies the data from the arduino
        self.frame.after(1000, self.getMainStorage)     # Will re-call this function every second
    
    def buttonOverride(self):
        print("Button disabled.")

