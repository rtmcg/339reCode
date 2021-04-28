# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 15:43:25 2018

@author: James Fraser

With code adapted from www.pythonprogramming.net

And Greg 2020-21

"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk


class Graph:
    def __init__(self, win, obj, row, verbose = 0):
        
## ================= MAIN GRAPHING OPTIONS ==============
        
        self.timeSlice = 10      # Graph every 10th piece of data
        self.updatePeriod = 500  # (ms) Period of often you want to update the graph via the self.root.after() callback
        
## =====================================================

        self.verbose = verbose
        if self.verbose : print("Initializing Graph object")


        self.root = win # Need these objects passed as arguments to allow the sharing of data between them
        self.obj = obj
        self.row = row

        self.yar = []   # y-axis array
        self.ylabel = self.obj.headerTable[self.row]    # Get y-label
        self.xar = []   # y-axis array
        self.xlabel = "TIME STEPS"        
        
        self.fig = Figure(figsize = (5,5), dpi = 100)   # Create figure object
        self.a = self.fig.add_subplot(111)              # Create and add a subplot to the figure object
        
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)  # This canvas is what we render the graph to
        self.canvas.draw() # shows plot # changed for python 3
        
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # puts widgets in blocks and places in tkinter matplotlib figure canvas, packs against top, fills all sides and expands to fill any space   
        
        self.animate() # Call the animate() function, which will call itself via self.root.after()

    def animate(self):
        if self.verbose : print("\n\nANIMATION CALL")        
        self.updateData()               # Acquire fresh data       
        if self.verbose : print("Y VALUES: ", self.yar)
        if self.verbose : print("X VALUES: ", self.xar)       
        self.a.clear()                  # Clear the subplot, to be replotted with fresh data      
        self.a.set_xlabel(self.xlabel)  # Set labels
        self.a.set_ylabel(self.ylabel)
        self.a.plot(self.xar, self.yar)  # Plot the data        
        self.canvas.draw() # draw canvas   
        self.root.after(self.updatePeriod, self.animate)  # Tells TKInter to call self.animate() after self.updatePeriod (ms)
        
    def updateData(self):  
        self.yar = []       # Clear array
        for tempRow in self.obj.mainStorage[1::self.timeSlice]: # For every block of data received by the Controller, take 1 in every self.timeSlice rows
            newPoint = tempRow[self.row]    # Add relevant data point based on self.row, it picks a specific set of elements
            self.yar.append(newPoint)       # Add to the Y-axis array
        self.xar = list(range(0, len(self.yar*self.timeSlice), self.timeSlice)) # Populate the X-axis array with appropriate values and skips