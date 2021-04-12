#!/usr/bin/env python 3
# -*- coding: utf-8 -*-
"""
This is only an example, it requires the LASER_2018.ino to be loaded on the Arduino
and it should be in the same folder as laserClass.py.

It does not imply what you need to do, merely implements a simple experiment that
gives an example interaction with the Arduino.

Be sure to wire your laser control card up to the true DAC.

Reviewed and updated Feb 2020
"""

#import string
import matplotlib.pyplot as p
import laserClass_python3_edit
import numpy as np

a = laserClass_python3_edit.Arduino()       # Begin instance of Arduino class
steps = 360                 # Synonymous with the number of measurements you wish you take
degsPerStep = 1             # This has to be calibrated by you       
a.send("LASER 1360")        # Laser control voltage
#a.send("STEPS %d"%(steps))  # Total number of steps
a.send(f"STEPS {steps}")  # Total number of steps
a.send("DELAY 4")          # Delay time before reading value (ms), >4 recommende
a.send("START")             # Start the stepping/reading
a.send("STOP")              # Sends a signal to change a variable on the arduino such that the motor stops after one full loop

arryAll = []    # Declare arrays for storing data.
stepCounts=[]   # Step indexes
adcValues = []  # ADC readings

index = -1
for k in range(steps):
    resp = a.getResp()
    if 9 == len(resp) and resp[4] == ':':
        arryAll.append(resp)               # Append raw response to array of raw serial data
        print("Got response ", resp, "\n")
            
        words = str.split(resp, ":")  # Split the response by the colon delimiter

        step = int(words[0])            # Note step count and append to appropriate array
        stepCounts.append(step)
        
        adc = int(words[1])            # Note A0 ADC value and append to appropriate array
        adcValues.append(adc)
    else:
        #print(("Unexpected response: %s"%(resp)))
        #print(("Length: %d"%(len(resp))))
        print(f"Unexpected response: {resp}")
        print(f"Length: {len(resp)}")        
    if 10 == index:
        break
        
stepCountsCal=np.array(stepCounts) * degsPerStep
adcValuesnp=np.array(adcValues)    
    
p.plot(stepCountsCal, adcValuesnp)    # Basic plot of ADC value per calibrated degree
                                             # Useful for a quick check of th data's quality

a.send("LASER 0")  # Shuts down laser
a.closePort()      # Closes port
print("Laser should have turned off by now")
