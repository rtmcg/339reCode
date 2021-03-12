from PyQt5 import QtCore, QtSerialPort
import matplotlib.pyplot as plt
import numpy as np


value = 100
arraySize = 10

app = QtCore.QCoreApplication([]) 
[print('port:', i.portName()) for i in QtSerialPort.QSerialPortInfo().availablePorts()]
serial_port = QtSerialPort.QSerialPort('COM3') 
# Use if baud rate not 9600
#serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud9600)
serial_port.open(QtCore.QIODevice.ReadWrite) 

print('serial port:' , serial_port)
print('description:',QtSerialPort.QSerialPortInfo(serial_port).description())
print('baud rate:' , serial_port.baudRate())
print('data bits:', serial_port.dataBits())
print('parity:' , serial_port.parity())
print('stop bits:', serial_port.StopBits())
print('DTR signal:', serial_port.DataTerminalReadySignal) 
print('flow controls:', serial_port.flowControl())

dataOut = []

def handle_ready_read(): 
    while serial_port.bytesAvailable(): 
        dataByte = serial_port.readLineData(1)
        dataOut.append(ord(dataByte))
        if len(dataOut) == arraySize:
            serial_port.close() 
            app.quit() 


serial_port.readyRead.connect(handle_ready_read) 

serial_port.write(bytes([value])) 

app.exec_()

plt.figure()
plt.plot(dataOut, 'o') 
plt.xlabel("array index")
plt.ylabel("8-bit rounded voltage reading")   
plt.show()
print('mean:', np.mean(dataOut))  

