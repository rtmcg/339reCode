# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018
    
@author: James Fraser

And Greg 2020-21
"""
#####============ IMPORT LIBRARIES =================####

import ArduinoClassForTemp_python3_edit4 # change if filename changes
import TkinterClass_python3_edit4 as tkc # change if filename changes
import tkinter as tk


#####============ OBJECT INITIALIZATION  ===========####

ard = ArduinoClassForTemp_python3_edit4.Arduino(device = 'COM4', verbose = 0)    # Create Arduino object for serial communications, and for data storage functionality
master = tk.Tk()   # Create frame object, so that we may access methods for creating a GUI via widgets (labels, entries, and buttons)                                   
ard.associate(master)     


#####============ INTERFACE ========================####
# Create GUI using tk.Tk() object and with functionality from Arduino object

GUI = tkc.Interface(master, ard, verbose = 0) 
         

#####============ THREAD ACTIVATION ================####
# Start the internal thread for each object, which lets Python run multiple loops at once

ard.thread.start()
tk.mainloop() # only call mainloop once, in the main thread, shouldn't make another thread, changed for python 3

