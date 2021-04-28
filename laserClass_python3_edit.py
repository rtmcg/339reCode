# -*- coding: utf-8 -*-
"""
This should be quite familiar by now. A simple script with some error checking
to open an arduino device and send/receive data from it.
"""

import serial


class Arduino:
    def __init__(self, device = 'COM3', verbose = 0): # device is COM port used with arduino
        self.verbose = verbose # get verbose class attribute
        if verbose: print("introArduino class creator: Verbose mode activated")
        #for i in range(2,10): # you may have to adjust range(1,10) depending on your COM ports
            #device = "COM%d" % (i) 
            #device = f"COM{i}" 
        try:
            self.device = serial.Serial(device, baudrate = 115200, timeout = 1.0) # serial port instance with baudrate and timeout set
            #if verbose: print("Found device at %s" % (device))
            if verbose: print(f"Found device at {device}")
            #break
        except:
            print('Device not found')
            #continue   
        self.device.setDTR(1); #reboot Arduino
        self.device.setDTR(0);
        self.device.setDTR(1);
        exception_count = 0
        attempts = 0
        while True: # runs until break or return
            try:
                if "LASER 2017" == self.getResp()[0:10]: # if the first part of the serial port response is this
                    if verbose: print("Arduino is communicating")
                    return # leaves loop because it leaves the init function
            except:
                if self.verbose: print("Exception")
                #exception_count = exception_count + 1
                exception_count += 1
            #attempts = attempts + 1 # redundant to have both exception_count and attempts counting, but it works
            attempts += 1 # redundant to have both exception_count and attempts counting, but it works
            if 5 == attempts:
                #print("Unable to communicate with Arduino...%d exceptions" % (exception_count))
                print(f"Unable to communicate with Arduino...{exception_count} exceptions")
                break # leave loop
    def send(self, strr): # changed str to strr, str is a built-in type
        #self.device.write("%s\n" % (str))
        strr = strr + '\n' # added for arduino code
        self.device.write(strr.encode()) # write to serial port after encoding to bytes
        #if self.verbose: print("Sent '%s'" % (str))
        if self.verbose: print(f"Sent '{strr}'")
    def getResp(self):
        if self.verbose: print("Waiting for response...")
        strr = self.device.readline().decode().split('\r\n')[0] # readline of serial port, bytes decoded, splits along \r\n and first element is taken
        #str = str.replace("\n","")
        #str = str.replace("\r","")
        #if self.verbose: print("Got response: '%s'" % (str))
        if self.verbose: print(f"Got response: '{strr}'")
        return strr
    def closePort(self):
        self.device.close() # close serial port
        print("Port is now closed")

#device = 'COM3'
#print(Arduino(device = device).getResp()) #check output
#print(Arduino(device = device).send("LASER 1360"))        