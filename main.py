import serial #pip install pyserial
from time import sleep
import matplotlib.pyplot as plt
from tkinter import *
import keyboard
import json

serial_object = serial.Serial('COM3', 115200, timeout=1, parity=serial.PARITY_NONE)
gui = Tk()
gui.title("PID Controller")

def Simpletoggle():
    if toggle_button.config('text')[-1] == 'ON':
        toggle_button.config(text='OFF')
        status.set(0)
    else:
        toggle_button.config(text='ON')
        status.set(1)
def send():
    send_data = data_entry.get()
    
    if not send_data:
        print("Sent Nothing")
    if status.get() == 1:
        send_data = "{:.2f}".format(float(send_data))
        send_data = str(data_entry.get())
        if len(send_data) == 4:
            send_data = send_data + '0'
        send_data =  send_data + 'A' +'\n'

        print("Ustawianie temperatury przez aplikacje")
        print(send_data)
        serial_object.write(send_data.encode())
       
    if status.get() == 0:
        print("Manualne ustawianie temperatury")
        send_data = "{:.2f}".format(float(send_data))
        send_data = str(data_entry.get())
        if len(send_data) == 4:
            send_data = send_data + '0'
        send_data =  send_data + 'M' + '\n'  
        print(send_data)
        serial_object.write(send_data.encode())
def plot():
    plt.ion()
    sleep(0.5)
    
    serial_object.reset_input_buffer()
    serial_object.flush()
    temperature_samples = [];
    temperatura_zadana_samples = [];

    t = [];
    t_value=0;
    while True:
        text = serial_object.readline()
        if not text:
            continue
        temperature = 0
        sample = 0
        try:
            sample = json.loads(text)
            temperature = sample["Temperatura"]
            temperatura_zadana = sample["TemperaturaZadana"]
            temperature_samples.append(temperature);
            temperatura_zadana_samples.append(temperatura_zadana);
            t.append(t_value);
            t_value = t_value + 1
            # Plot results
            plt.clf()
            plt.plot(t,temperature_samples, markersize=5);
            plt.plot(t,temperatura_zadana_samples, markersize=5);
            plt.title("Wykres temperatury")
            plt.xlabel("Czas (s)")
            plt.ylabel("Temperatura (C)")
            plt.legend(["Temperatura", "Temperatura zadana"])
            plt.show()
            plt.pause(1)
            print(temperature)
        except ValueError:
            print("Bad JSON")
            print("%s\r\n" % {text})
            serial_object.flush()
            serial_object.reset_input_buffer()
    

        if keyboard.is_pressed("q"):
            break  # finishing the loop
        
data_entry = Scale(from_=20, to=40, orient=HORIZONTAL, resolution=0.01, length=300)
data_entry.place(x = 100, y = 0)
button1 = Button(text = "Wyślij temperaturę zadaną", command = send, width = 30).place(x = 100, y = 50)
button2 = Button(text = "Wykres temperatury", command = plot, width = 30).place(x = 100, y = 100)

status = IntVar()
toggle_button = Button(text="OFF", width=10, command=Simpletoggle)
toggle_button.pack(side=BOTTOM,pady=10)
l = Label(text="Zadawanie temperatury z aplikacji", font=("Helvetica", 14)).place(x = 100, y = 425)

gui.geometry('500x500')
gui.mainloop()