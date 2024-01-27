import serial #pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from tkinter import ttk
from tkinter import *
import keyboard
import re
serial_object = serial.Serial('COM3', 115200, timeout=1, parity=serial.PARITY_NONE)
gui = Tk()
gui.title("PID Controller")

def send():
    send_data = data_entry.get()
    
    if not send_data:
        print("Sent Nothing")
    if status.get() == 1:
        serial_object.write(send_data.encode())
    else:
        print("Manualne ustawianie temperatury")

data_entry = Entry()
data_entry.place(x = 100, y = 255)
button1 = Button(text = "Send", command = send, width = 6).place(x = 15, y = 250)
status = IntVar()
check1 = Checkbutton(text = "Ustawiaj temperaturę przez aplikacje", variable=status).place(x = 15, y = 280)
gui.geometry('500x500')
gui.mainloop()

serial_object.reset_input_buffer()
serial_object.flush()
temperature_samples = [];
t = [];
t_value=0;
temperature = 0
while True:
    text = serial_object.readline()
    sample = 0
    decoded_string = text.decode("utf-8")
    x123 = str(re.findall("\d+.\d+",decoded_string))
    x123 = x123.replace('[','')
    x123 = x123.replace(']','')
    x123 = x123.replace(')','')
    x123 = x123.replace('(','')
    x123 = x123.replace("'","")
    if len(x123) < 6:
        temperature = float(x123)
    print(temperature)
    temperature_samples.append(temperature);
    if keyboard.is_pressed("q"):
        break  # finishing the loop
serial_object.close()
