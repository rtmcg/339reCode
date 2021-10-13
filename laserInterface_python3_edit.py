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
import matplotlib.pyplot as plt
import laserClass_python3_edit
import numpy as np

device = 'COM6' # COM port set on arduino
a = laserClass_python3_edit.Arduino(device = device, verbose = 0)       # Begin instance of Arduino class
steps = 3600                 # Synonymous with the number of measurements you wish you take
degsPerStep = 1             # This has to be calibrated by you       
a.send("LASER 1350")        # Laser control voltage
#a.send("STEPS %d"%(steps))  # Total number of steps
a.send(f"STEPS {steps}")  # Total number of steps
a.send("DELAY 4")          # Delay time before reading value (ms), >4 recommende
a.send("START")             # Start the stepping/reading
a.send("STOP")              # Sends a signal to change a variable on the arduino such that the motor stops after one full loop

arryAll = []    # Declare arrays for storing data.
stepCounts = []   # Step indexes
adcValues = []  # ADC readings

index = -1 # I'm not sure the point of this, the index is not incremented, maybe set it to 10 if leaving the loop after one time is wanted, it is used in the graphing code
for k in range(steps):
    resp = a.getResp() # get a readline
    if 9 == len(resp) and resp[4] == ':': # if the length of the response is 9 and the 4 index of it is :
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
    if 10 == index: # could leave loop after one time if this were set to 10
        break # leave loop
        
stepCountsCal = np.array(stepCounts) * degsPerStep # multiply array of stecounts by degsperstep
adcValuesnp = np.array(adcValues) # make array of adcvalues
    
plt.plot(stepCountsCal, adcValuesnp)    # Basic plot of ADC value per calibrated degree
                                             # Useful for a quick check of th data's quality

a.send("LASER 0")  # Shuts down laser
a.closePort()      # Closes port
print("Laser should have turned off by now")
