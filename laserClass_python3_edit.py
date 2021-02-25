# -*- coding: utf-8 -*-
"""
This should be quite familiar by now. A simple script with some error checking
to open an arduino device and send/receive data from it.
"""

import serial


class Arduino:
    def __init__(self,verbose=0):
        self.verbose = verbose
        if verbose: print("introArduino class creator: Verbose mode activated")
        for i in range(1,10): #you maay have to adjust range(1,10) depending on your COM ports
            device = "COM%d" % (i) 
            try:
                self.device = serial.Serial(device,baudrate=115200,timeout=1.0) 
                if verbose: print("Found device at %s" % (device))
                break
            except:
                continue   
        self.device.setDTR(1); #reboot Arduino
        self.device.setDTR(0);
        self.device.setDTR(1);
        exception_count = 0
        attempts = 0
        while True:
            try:
                if "LASER 2017" == self.getResp()[0:10]: 
                    if verbose: print("Arduino is communicating")
                    return
            except:
                if self.verbose: print("Exception")
                exception_count = exception_count + 1
            attempts = attempts + 1
            if 5 == attempts:
                print("Unable to communicate with Arduino...%d exceptions" % (exception_count))
                break
    def send(self,str):
        #self.device.write("%s\n" % (str))
        str = str + '\n'
        self.device.write(str.encode())
        if self.verbose: print("Sent '%s'" % (str))
    def getResp(self):
        if self.verbose: print("Waiting for response...")
        str = self.device.readline().decode().split('\r\n')[0] 
        #str = str.replace("\n","")
        #str = str.replace("\r","")
        if self.verbose: print("Got response: '%s'" % (str))
        return str
    def closePort(self):
        self.device.close()
        print("Port is now closed")

#print(Arduino().getResp()) #check output
#print(Arduino().send("LASER 1360"))        