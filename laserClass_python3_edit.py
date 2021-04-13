# -*- coding: utf-8 -*-
"""
This should be quite familiar by now. A simple script with some error checking
to open an arduino device and send/receive data from it.
"""

import serial


class Arduino:
    def __init__(self, verbose=0):
        self.verbose = verbose
        if verbose: print("introArduino class creator: Verbose mode activated")
        #for i in range(2,10): # you may have to adjust range(1,10) depending on your COM ports
            #device = "COM%d" % (i) 
            #device = f"COM{i}" 
        device = 'COM4' # COM port used for Arduino
        try:
            self.device = serial.Serial(device, baudrate=115200, timeout=1.0) 
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
                #print("Unable to communicate with Arduino...%d exceptions" % (exception_count))
                print(f"Unable to communicate with Arduino...{exception_count} exceptions")
                break
    def send(self, strr): # changed str to strr, str is a built-in type
        #self.device.write("%s\n" % (str))
        strr = strr + '\n'
        self.device.write(strr.encode())
        #if self.verbose: print("Sent '%s'" % (str))
        if self.verbose: print(f"Sent '{strr}'")
    def getResp(self):
        if self.verbose: print("Waiting for response...")
        strr = self.device.readline().decode().split('\r\n')[0] 
        #str = str.replace("\n","")
        #str = str.replace("\r","")
        #if self.verbose: print("Got response: '%s'" % (str))
        if self.verbose: print(f"Got response: '{strr}'")
        return strr
    def closePort(self):
        self.device.close()
        print("Port is now closed")

#print(Arduino().getResp()) #check output
print(Arduino().send("LASER 1360"))        