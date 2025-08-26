import serial
import serial.tools.list_ports

class ArduinoInstrument(serial.Serial):
    def __init__(self, 
                 port=None, 
                 baudrate=115200, 
                 bytesize=serial.EIGHTBITS, 
                 parity=serial.PARITY_NONE, 
                 stopbits=serial.STOPBITS_ONE, 
                 timeout=5.0, 
                 xonxoff=False, 
                 rtscts=False, 
                 writeTimeout=5.0, 
                 dsrdtr=False, 
                 interCharTimeout=None):
        arduino_port = None
        if port == 'auto':
            ports = list(serial.tools.list_ports.grep('(Arduino)|(VID:PID=2341)'))
            if len(ports) == 1:
                # found it
                arduino_port = ports[0].device
            elif len(ports) > 1:
                # multiple possibilities
                raise ArduinoError(f'Multiple Arduinos found: {ports}')
            else:
                raise ArduinoError('No Arduino found.')
        else:
            arduino_port = port
        super().__init__(arduino_port, baudrate, bytesize, parity, 
                         stopbits, timeout, xonxoff, rtscts, writeTimeout, 
                         dsrdtr, interCharTimeout)
        self.frame_count = 1
        
    def writeline(self, *args):
        strings = [str(i) for i in args]
        data = ' '.join(strings) + '\n'  # Append newline character
        print(f"Sending data to Arduino: {data}")
        self.write(data.encode())
        
    def readline(self):
        self._last_read = super().readline().decode()
        print(f"Raw data read from Arduino: {self._last_read}")
        if self._last_read == '':
            raise serial.SerialTimeoutException('Timeout when waiting for Serial.readline().')
        return self._last_read.strip()
        
    def ask(self, *args, **kwargs):
        self.writeline(*args)
        return self.readline(**kwargs)
    
class ArduinoCommunicationError(Exception):
    pass

class ArduinoError(Exception):
    pass
