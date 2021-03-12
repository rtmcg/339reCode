
from PyQt5 import QtCore, QtSerialPort

#import sys # used if sys.exit() is used

value = 100
arraySize = 500

app = QtCore.QCoreApplication([]) 

#[print('port:', i.portName()) for i in QtSerialPort.QSerialPortInfo().availablePorts()]
serial_port = QtSerialPort.QSerialPort('COM3') 

#serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud9600)

serial_port.open(QtCore.QIODevice.ReadWrite) 

# =============================================================================
# print('serial port:' , serial_port)
# print('description:',QtSerialPort.QSerialPortInfo(serial_port).description())
# print('baud rate:' , serial_port.baudRate())
# print('data bits:', serial_port.dataBits())
# print('parity:' , serial_port.parity())
# print('stop bits:', serial_port.StopBits())
# print('DTR signals:', serial_port.DataTerminalReadySignal) 
# print('flow controls:', serial_port.flowControl())
# =============================================================================

dataOut = []

def handle_ready_read(): 
    while serial_port.bytesAvailable(): 
        dataByte = serial_port.readLineData(1)
        #print(dataByte)
        dataOut.append(ord(dataByte))
        #dataOut.append(dataByte)
        if len(dataOut) == arraySize:
            serial_port.close() 
            #Plot your analog output!

            app.quit() 
        #serial_port.write(bytes([value]))


serial_port.readyRead.connect(handle_ready_read) 

serial_port.write(bytes([value])) 

#sys.exit(app.exec_()) 
app.exec_()
print(dataOut) 

