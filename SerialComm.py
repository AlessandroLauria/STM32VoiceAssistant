
#!/usr/bin/env python 
      
import time
import serial

class SerialComm:
    
    def __init__(self, port, baudrate):
                
        self.ser = serial.Serial(            
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        
    def send(self, msg):
        if msg:
            try:
                self.ser.write((msg+"\n").encode())
            except Exception as e:
                print("[SERIAL ERROR] ", e)
                
    def read(self):
        try:
            return self.ser.readline().decode()
        except Exception as e:
            print("[SERIAL ERROR] ", e)
    
#ser = SerialComm('/dev/ttyACM0', 9600)   
#while True:
#    print("mando")
#    ser.send("ciao sono raspi")
#    print("read: ", ser.read())
#    time.sleep(1)
         