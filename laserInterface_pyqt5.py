from PyQt5 import QtCore, QtSerialPort, QtWidgets 
import matplotlib.pyplot as plt
import numpy as np
import sys

steps = 360
degsPerStep = 1     # This has to be calibrated by you 
verbose = 0         # if want to see more details

arryAll = []        # Declare arrays for storing data.
stepCounts=[]       # Step indexes
adcValues = []      # ADC readings
device = 'COM4'     # Set COM port used by arduino

attempts = []
connected = False

if verbose: print("Verbose mode activated")

# word wrap can be set in spyder, wrap lines in display editor preferences
# ctrl-4 and ctrl-5 can be used to comment in out and blocks of code
# This can be used with inline, instead of commenting out app.setQuitOnLastWindowClosed(True) 
# =============================================================================
# class CoreApplication(QtCore.QCoreApplication):
#     def setQuitOnLastWindowClosed(self, quit):
#         pass
# 
# app = CoreApplication([])
# =============================================================================

# with pyqt, automatic backend graphics can cause conflicts
# since the window may use Qt
#app = QtCore.QCoreApplication([]) # use with inline plotting

app = QtWidgets.QApplication([]) # use with automatic plotting

serial_port = QtSerialPort.QSerialPort(device) # COM? choose COM port number

serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud115200)
isopen = serial_port.open(QtCore.QIODevice.ReadWrite) 

if isopen:
    if verbose: print(f'Device found at {device}')
    
else:
    print('Device not found')
    serial_port.close()
    app.quit()
    sys.exit()


serial_port.setDataTerminalReady(1)
serial_port.setDataTerminalReady(0)
serial_port.setDataTerminalReady(1)
print('serial port:' , serial_port)
print('description:',QtSerialPort.QSerialPortInfo(serial_port).description())
print('baud rate:' , serial_port.baudRate())
print('data bits:', serial_port.dataBits())
print('parity:' , serial_port.parity())
print('stop bits:', serial_port.StopBits())
print('DTR signal:', serial_port.DataTerminalReadySignal) 
print('flow control:', serial_port.flowControl())
print('is DTR' , serial_port.isDataTerminalReady())

def send(text):
    text = text + '\n'
    serial_port.write(text.encode())
    if verbose: print(f"Sent '{text}'")

def handle_ready_read(): 
    global connected
    while serial_port.canReadLine():
        if verbose: print('Waiting for response...')
        resp = serial_port.readLine().data().decode().strip()
        #resp = serial_port.readLine().data().decode('ISO-8859-1').replace('\n','').replace('\r','').strip() # another way to read data
        if verbose: print(f"Got response: '{resp}'")
        if connected == False and resp == "LASER 2017":
            
            if verbose: print("Arduino is communicating")
            connected = True
            send("LASER 1360") # Laser control voltage
            send(f"STEPS {steps}") # Total number of steps
            send("DELAY 4") # Delay time before reading value (ms), >4 recommende
            send("START") # Start the stepping/reading
            send("STOP") # Sends a signal to change a variable on the arduino such that the motor stops after one full loop
        
        elif connected == False and len(attempts) < 5:
            
            if verbose: print("Exception")
            attempts.append(1)
        
        elif connected == False and len(attempts) == 5:
            
            print("Unable to communicate with Arduino...5 exceptions")
            send("LASER 0") 
            serial_port.setDataTerminalReady(0)
            serial_port.setDataTerminalReady(1)
            serial_port.setDataTerminalReady(0)
            serial_port.close()
            app.quit()            
            
        if 9 == len(resp) and resp[4] == ':':

            arryAll.append(resp)               # Append raw response to array of raw serial data
            print("Got response ", resp, "\n")
                
            words = str.split(resp, ":")  # Split the response by the colon delimiter
    
            step = int(words[0])            # Note step count and append to appropriate array
            stepCounts.append(step)
            
            adc = int(words[1])            # Note A0 ADC value and append to appropriate array
            adcValues.append(adc)
        
        else:
            
            print(f"Unexpected response: {resp}")
            print(f"Length: {len(resp)}")   
        
        if len(stepCounts) == steps:
            stepCountsCal=np.array(stepCounts) * degsPerStep
            adcValuesnp=np.array(adcValues)    
    
            plt.plot(stepCountsCal, adcValuesnp)    # Basic plot of ADC value per calibrated degree
                                             # Useful for a quick check of th data's quality
            print('Closing port')
            send("LASER 0") 
            serial_port.setDataTerminalReady(0)
            serial_port.setDataTerminalReady(1)
            serial_port.setDataTerminalReady(0)
            serial_port.close()
            #app.quit() # If automatic backend is set, this is not needed and it would close the plot quickly, with inline it is, the latter using app = QtCore.QCoreApplication([])  

        if resp == 'Timeout!':
            
            print('Timeout occured, closing')
            send("LASER 0") 
            serial_port.setDataTerminalReady(0)
            serial_port.setDataTerminalReady(1)
            serial_port.setDataTerminalReady(0)
            serial_port.close()
            app.quit()             

serial_port.clear()  

serial_port.readyRead.connect(handle_ready_read) 
 
app.setQuitOnLastWindowClosed(True) # comment out if using inline graphics backend

sys.exit(app.exec_())

