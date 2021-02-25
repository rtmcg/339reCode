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
import matplotlib.pyplot as p
import laserClass_python3_edit

a = laserClass_python3_edit.Arduino() 
steps = 360
degsPerStep = 1           # This has to be calibrated by you       
a.send("LASER 1280")        # Laser control voltage
a.send("STEPS %d"%(steps))  # Total number of steps
a.send("DELAY 4")         # Delay time before reading value (ms), >4 recommended
a.send("START")             # Start the stepping/reading
a.send("STOP")
vector = np.zeros(steps)
index = -1
for k in range(steps):
    resp = a.getResp()
    if 9 == len(resp) and resp[4] == ':':
        words = str.split(resp,":")
        step = int(words[0])
        adc = int(words[1])
        if 0 == step:
            p.ion()
            fig = p.figure()
            p.xlabel("Step index")
            p.ylabel("ADC reading")
            ax = fig.add_subplot(111)
            lines, = ax.plot(list(range(k+1)),vector[:k+1])  
            p.axis([0,steps,0,max(vector)])
            #lines, = ax.plot(np.array(range(k+1))*degsPerStep,vector[:k+1])  
            #p.axis([0,steps*degsPerStep,0,max(vector)])
            p.pause(0.01)      
            index += 1
        vector[step] = adc
        lines.set_data(list(range(k+1)),vector[:k+1])
        p.axis([0,steps,0,max(vector)])
        #lines.set_data(np.array(range(k+1))*degsPerStep,vector[:k+1])
        #p.axis([0,steps*degsPerStep,0,max(vector)])
        p.pause(0.01)      
    else:
        print(("Unexpected response: %s"%(resp)))
        print(("Length: %d"%(len(resp))))
    if 10 == index:
        break
a.send("LASER 0")
a.closePort()   