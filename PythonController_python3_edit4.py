# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 09:18:21 2018
    
@author: James Fraser

"""
#####============ IMPORT LIBRARIES =================####

import ArduinoClassForTemp_python3_edit4 #changed for python3
import TkinterClass_python3_edit4 as tkc #changed for python3
import tkinter as tk
#from mttkinter import mtTkinter as tk #trying out

#####============ OBJECT INITIALIZATION  ===========####

ard = ArduinoClassForTemp_python3_edit4.Arduino(verbose = 1)    # Create Arduino object for serial communications, and for data storage functionality
master = tk.Tk()   # Create frame object, so that we may access methods for creating a GUI via widgets (labels, entries, and buttons)                                   
ard.associate(master)     


#####============ INTERFACE ========================####
# Create GUI using tk.Tk() object and with functionality from Arduino object

GUI = tkc.Interface(master,ard, verbose = 1 ) 
         

#####============ THREAD ACTIVATION ================####
# Start the internal thread for each object, which lets Python run multiple loops at once

ard.thread.start()
tk.mainloop() # replaces next line, only call mainloop once, in the main thread, shouldn't make another thread
#GUI.thread.start()
