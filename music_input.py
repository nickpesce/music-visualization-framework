import serial
import numpy as np

class Input:
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.open()

    def receive_input(self, func):
        self.listener = func

    def start_listening(self):
        while self.ser.isOpen():
            byte_line = self.ser.readline()
            try:
                line = np.array(byte_line.decode().strip().split('|')).astype(int)
                self.listener(line)
            except (UnicodeDecodeError, ValueError) as e:
                print("Error", e)
