import math

import serial  # pip install pyserial
import numpy as np
from time import sleep
import time
import json
import matplotlib.pyplot as plt
import keyboard  # pip install keyboard
import cv2
import sys

plt.ion()

hSerial = serial.Serial('COM3', 115200, timeout=1, parity=serial.PARITY_NONE)
sleep(0.5)
timestr = time.strftime("%Y%m%d-%H%M%S")
hFile = open("data_two_position_controller_%s.txt" % (timestr), "a")

hSerial.reset_input_buffer()
hSerial.flush()
temperature_samples = [];
pwm_samples = []
reference_samples = []
temperature_analog_samples = []
t = [];
t_value = 0;
run = True
text = hSerial.readline()
kpInitial = 20
kiInitial = 0.25
tempInitial = 20

try:
    sample = json.loads(text)
    kpInitial = sample["kp"]
    kiInitial = sample["ki"]
    tempInitial = sample["reference"]
except ValueError:
    print("Bad JSON")
    print("%s\r" % {text})
    hSerial.flush()
    hSerial.reset_input_buffer()

kpValue = math.floor((kpInitial * 100) / 20)
kpPrevious = math.floor((kpInitial * 100) / 20)
kpSent = True

kiValue = math.floor((kiInitial * 100) / 0.25)
kiPrevious = math.floor((kiInitial * 100) / 0.25)
kiSent = True

referenceValue = math.floor((tempInitial - 20) * 10)
referencePrevious = math.floor((tempInitial - 20) * 10)
referenceSent = True

cv2.namedWindow('Manage PI')
cv2.createTrackbar('kp %', 'Manage PI', kpValue, 1000, lambda _: None)
cv2.createTrackbar('ki %', 'Manage PI', kiValue, 1000, lambda _: None)
cv2.createTrackbar('reference 20 + x/10', 'Manage PI', referenceValue, 200, lambda _: None)

while run:
    text = hSerial.readline()
    textString = text.decode("utf-8")
    print(textString)
    temperature = 0
    sample = 0
    pwm = 0
    reference = 0
    temperatureAnalog = 0

    kpPrevious = kpValue
    kiPrevious = kiValue
    referencePrevious = referenceValue
    kpValue = cv2.getTrackbarPos('kp %', 'Manage PI')
    kiValue = cv2.getTrackbarPos('ki %', 'Manage PI')
    referenceValue = cv2.getTrackbarPos('reference 20 + x/10', 'Manage PI')

    if (kpPrevious != kpValue):
        kpSent = False

    if (kiPrevious != kiValue):
        kiSent = False

    if (referenceValue != referencePrevious):
        referenceSent = False

    if ((not kpSent) and (kpValue == kpPrevious)):
        stringToSend = f'kp={kpValue * 20 / 100};'
        hSerial.write(stringToSend.encode())
        print('changed kp')
        kpSent = True

    if ((not kiSent) and (kiValue == kiPrevious)):
        stringToSend = f'ki={kiValue * 0.25 / 100};'
        hSerial.write(stringToSend.encode())
        print('changed kp')
        kiSent = True

    if ((not referenceSent) and (referenceValue == referencePrevious)):
        stringToSend = f'temp={referenceValue / 10 + 20};'
        hSerial.write(stringToSend.encode())
        print('changed reference')
        referenceSent = True

    try:
        sample = json.loads(text)
        temperature = sample["temperature"]
        reference = sample["reference"]
        pwm = sample["pwm"]
        temperatureAnalog = sample["temperatureAnalog"]
        hFile.write("%s" % textString)
    except ValueError:
        print("Bad JSON")
        print("%s\r" % {text})
        hSerial.flush()
        hSerial.reset_input_buffer()

    temperature_samples.append(temperature)
    temperature_analog_samples.append(temperatureAnalog)
    pwm_samples.append(pwm)
    reference_samples.append(reference)
    t.append(t_value);
    t_value = t_value + 1
    # Plot results
    plt.figure('Temperature')
    plt.clf()
    plt.plot(t, temperature_samples, '.', markersize=5, label="Temperature")
    plt.title("Temperatura")
    plt.ylabel("$^\circ$C")
    plt.xlabel("Czas (s)")
    plt.legend()

    plt.figure('TemperatureAnalog')
    plt.clf()
    plt.plot(t, temperature_analog_samples, '.', markersize=5, label="Temperature")
    plt.title("Temperatura analog")
    plt.ylabel("$^\circ$C")
    plt.xlabel("Czas (s)")
    plt.legend()

    plt.figure('PWM')
    plt.ylabel("%")
    plt.clf()
    plt.plot(t, pwm_samples, '.', markersize=5, label="PWM")
    plt.title("Sygnał PWM")
    plt.ylabel("%")
    plt.xlabel("Czas (s)")
    plt.legend()

    plt.figure('Reference')
    plt.clf()
    plt.plot(t, reference_samples, '.', markersize=5, label="Reference")
    plt.title("Sygnał Referencyjnego")
    plt.ylabel("$^\circ$C")
    plt.xlabel("Czas (s)")
    plt.legend()
    plt.pause(0.3)
    plt.show()

    if keyboard.is_pressed("q"):
        run = False  # finishing the loop
        cv2.destroyAllWindows()

hSerial.close()
hFile.close()
