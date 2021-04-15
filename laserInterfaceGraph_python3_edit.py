#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is only an example, it requires the LASER_2018.ino to be loaded on the Arduino
and it should be in the same folder as Arduino.py.

It does not imply what you need to do, merely implements a simple exerpiment that
gives an example interaction with the Arduino.
"""

import numpy as np
#import string
import matplotlib.pyplot as plt
import laserClass_python3_edit

device = 'COM4' # COM port used with arduino
a = laserClass_python3_edit.Arduino(device = device, verbose = 0) 
steps = 360 
degsPerStep = 1           # This has to be calibrated by you       
a.send("LASER 1280")        # Laser control voltage
#a.send("STEPS %d"%(steps))  # Total number of steps
a.send(f"STEPS {steps}")  # Total number of steps
a.send("DELAY 4")         # Delay time before reading value (ms), >4 recommended
a.send("START")             # Start the stepping/reading
a.send("STOP")
vector = np.zeros(steps)
index = -1
for k in range(steps):
    resp = a.getResp()
    if 9 == len(resp) and resp[4] == ':':
        words = str.split(resp, ":")
        step = int(words[0])
        adc = int(words[1])
        if 0 == step:
            #plt.ion() # can be used or not
            fig = plt.figure()
            #plt.xlabel("Step index") # setting label with ax
            #plt.ylabel("ADC reading")
            ax = fig.add_subplot(111)
            ax.set_xlabel("Step index")
            ax.set_ylabel("ADC reading")
            lines, = ax.plot(list(range(k+1)), vector[:k+1])  
            #ax.set_xlim(0, steps)
            #ax.set_ylim(0, max(vector)) # max(vector) is 0 here
            #plt.axis([0, steps, 0, max(vector)]) # set axis limits with ax
            #lines, = ax.plot(np.array(range(k+1))*degsPerStep, vector[:k+1])  
            #plt.axis([0, steps*degsPerStep, 0, max(vector)])
            #ax.set_xlim(0, steps*degsPerStep)
            #ax.set_ylim(0, max(vector)) # max(vector) is 0 here
            plt.pause(0.01)      
            index += 1
        vector[step] = adc
        lines.set_data(list(range(k+1)), vector[:k+1])
        #plt.axis([0, steps, 0, max(vector)])
        ax.set_xlim(0, steps)
        ax.set_ylim(0, max(vector))
        #lines.set_data(np.array(range(k+1))*degsPerStep, vector[:k+1])
        #plt.axis([0, steps*degsPerStep, 0, max(vector)])
        #ax.set_xlim(0, steps*degsPerStep)
        #ax.set_ylim(0, max(vector))
        plt.pause(0.01)      
    else:
        #print(("Unexpected response: %s"%(resp)))
        #print(("Length: %d"%(len(resp))))
        print(f"Unexpected response: {resp}")
        print(f"Length: {len(resp)}") 
    if 10 == index:
        break
a.send("LASER 0")
a.closePort()   