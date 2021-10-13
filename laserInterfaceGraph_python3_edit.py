#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is only an example, it requires the LASER_2018.ino to be loaded on the Arduino
and it should be in the same folder as Arduino.py.

It does not imply what you need to do, merely implements a simple exerpiment that
gives an example interaction with the Arduino.

2021.04.30 - the lastest testing of this code was done with 2021LaserArduino.ino,
which is in Robert's folder Q:\subDirs\0-courses\339\339-4-Laser
"""

import numpy as np
#import string
import matplotlib.pyplot as plt
import laserClass_python3_edit

device = 'COM6' # COM port used with arduino
a = laserClass_python3_edit.Arduino(device = device, verbose = 0) # instance of arduino class
steps = 360
degsPerStep = 1           # This has to be calibrated by you       
a.send("LASER 1400")        # Laser control voltage
#a.send("STEPS %d"%(steps))  # Total number of steps
a.send(f"STEPS {steps}")  # Total number of steps
a.send("DELAY 20")         # Delay time before reading value (ms), >4 recommended
a.send("START")             # Start the stepping/reading
a.send("STOP")              # Sends a signal to change a variable on the arduino such that the motor stops after one full loop
vector = np.zeros(steps) # create vector of 0's of length steps
index = -1 # used to end loop if proper values aren't obtained from arduino

for k in range(steps): # loop through length steps
    # added ramping output for testing 20210429-rt
    # begin testing
    # llim = 1146
    # ulim = 1520
    # band = ulim-llim
    # scale = band/steps
    # sendlaservalue = int(k*scale + llim)
    # print(k, sendlaservalue)
    # a.send(f"LASER {int(sendlaservalue)}")
    # end testing
    resp = a.getResp() # get readline from arduino
    if 9 == len(resp) and resp[4] == ':': # if length of resp is 9 and index 4 gives :
        words = str.split(resp, ":") # split the response along :
        step = int(words[0]) # the first element as int, before :
        adc = int(words[1]) # the second element as int, after :
        if 0 == step: # if the first element is 0
            #plt.ion() # can be used or not
            fig = plt.figure() # create figure
            #plt.xlabel("Step index") # setting label with ax
            #plt.ylabel("ADC reading")
            ax = fig.add_subplot(111) # add subplot to figure
            ax.set_xlabel("Step index") # set x label
            ax.set_ylabel("ADC reading") # set y label
            lines, = ax.plot(list(range(k+1)), vector[:k+1]) # plot the vector up to current step (k), with index for x axis  
            #ax.set_xlim(0, steps)
            #ax.set_ylim(0, max(vector)) # max(vector) is 0 here
            #plt.axis([0, steps, 0, max(vector)]) # set axis limits with ax
            #lines, = ax.plot(np.array(range(k+1))*degsPerStep, vector[:k+1])  # if degsperstep is used
            #plt.axis([0, steps*degsPerStep, 0, max(vector)]) # if degsperstep is used
            #ax.set_xlim(0, steps*degsPerStep)
            #ax.set_ylim(0, max(vector)) # max(vector) is 0 here
            plt.pause(0.01)      # pause the plotting, or else freezes
            index += 1 # increment index, in case keep receiving step == 0
        vector[step] = adc # fill the vector with adc values for each step
        lines.set_data(list(range(k+1)), vector[:k+1]) # set the new plot data with the values added to vector
        #plt.axis([0, steps, 0, max(vector)])
        ax.set_xlim(0, steps) # set the x limit of the plot with full number of steps
        ax.set_ylim(min(vector)-100, max(vector)+100) # set the y limit with the max adc value
        #lines.set_data(np.array(range(k+1))*degsPerStep, vector[:k+1]) # if degsperstep is used
        #plt.axis([0, steps*degsPerStep, 0, max(vector)]) # if degsperstep is used
        #ax.set_xlim(0, steps*degsPerStep)
        #ax.set_ylim(0, max(vector))
        plt.pause(0.01)      # pause the plot
    else:
        #print(("Unexpected response: %s"%(resp)))
        #print(("Length: %d"%(len(resp))))
        print(f"Unexpected response: {resp}")
        print(f"Length: {len(resp)}") 
    if 10 == index: # if keep getting step == 0, leave loop
        break


a.send("LASER 0") # shut down laser
a.closePort()   # close serial port