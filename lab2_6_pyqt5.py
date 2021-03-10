# PyQt5 is a comprehensive set of Python bindings for Qt v5.
# Qt is a full development framework with tools designed to streamline the 
# creation of applications and user interfaces for desktop, embedded, and mobile platforms.
# see https://doc.qt.io/qt-5/qserialport.html
# Import QtSerialPort and QtCore libraries from PyQt5 
from PyQt5 import QtCore, QtSerialPort
# sys provides access to some variables used or maintained by the interpreter
# and to functions that interact strongly with the interpreter
import sys # used if sys.exit() is used
# 8-bit value to be written to PWB pin
value = 130
# Used by non-GUI apps to provide the event loop
app = QtCore.QCoreApplication([]) 
# Prints serial ports available
[print('port:', i.portName()) for i in QtSerialPort.QSerialPortInfo().availablePorts()]
# Creates serial port object with the port name 'COM?'
serial_port = QtSerialPort.QSerialPort('COM3') 
# Set the baud rate at 9600
serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud9600)
# Opens the serial port using the read/write mode
serial_port.open(QtCore.QIODevice.ReadWrite) 
# Print serial port specifications
print('serial port:' , serial_port)
print('description:',QtSerialPort.QSerialPortInfo(serial_port).description())
print('baud rate:' , serial_port.baudRate())
print('data bits:', serial_port.dataBits())
print('parity:' , serial_port.parity())
print('stop bits:', serial_port.StopBits())
print('pin out signals:', serial_port.pinoutSignals()) # signals can be printed 
# from https://doc.qt.io/qt-5/qserialport.html#PinoutSignal-enum
print('flow controls:', serial_port.flowControl())
# Qt slot function connected to readRead
def handle_ready_read(): 
    # True is data can be read from the serial port
    while serial_port.canReadLine(): 
        #print(serial_port.readLine().data().decode().strip())
        # Readline reads ASCII characters from the arduino, b'W\r\n',
        # and stores them in data as a QByteArray, which is thus called.
        # decode() decodes the bytes to a string object.
        # Strip gets rid of whitespaces,
        # since println from arduino includes a '\r' and a '\n'.
        if serial_port.readLine().data().decode().strip() == 'W': 
            # Closes the serial port connection
            serial_port.close() 
            # Quits the Qt app event loop
            app.quit() 

# Qt signal emitted each time data is available for reading from arduino
serial_port.readyRead.connect(handle_ready_read) 
# Write to the serial port
serial_port.write(bytes([value])) 
# Starts the qt app event loop
#app.exec_() 
# starts the event loop and quits the program when finished
sys.exit(app.exec_()) 
# However, the while loop ends after the only line read is read
# and the serial port is closed and the Qt event loop is ended when 'W' is read
# if there are errors the program may not end, but then try statements
# and other error checking would need to be added if errors were to be accounted for