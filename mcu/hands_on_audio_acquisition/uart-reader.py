# -*- coding: utf-8 -*-
"""
uart-reader.py
ELEC PROJECT - 210x
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np
import serial
import soundfile as sf
from serial.tools import list_ports

PRINT_PREFIX = "SND:HEX:"
FREQ_SAMPLING = 10200
VAL_MAX_ADC = 4096
VDD = 3.3


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=1042).decode("ascii")
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            dt = np.dtype(np.uint16)
            dt = dt.newbyteorder("<")
            buffer_array = np.frombuffer(buffer, dtype=dt)

            yield buffer_array


def generate_audio(buf, file_name):
    buf = np.asarray(buf, dtype=np.float64)
    buf = buf - np.mean(buf)
    buf /= max(abs(buf))
    sf.write("audio_files/" + file_name + ".ogg", buf, FREQ_SAMPLING)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()
    print("uart-reader launched...\n")

    #argParser.add_argument("-f", "--fourier",action='store_true', help="For the part 2, plot the Fourier Transform. Launch this script with [-f]")
   
    if args.port is None:
        print(
            "No port specified, here is a list of serial communication port available"
        )
        print("================")
        port = list(list_ports.comports())
        for p in port:
            print(p.device)
        print("================")
        print("Launch this script with [-p PORT_REF] to access the communication port")

    else:
        plt.figure(figsize=(10, 5))
        input_stream = reader(port=args.port)
        msg_counter = 0

        for msg in input_stream:
            print("Acquisition #{}".format(msg_counter))

            buffer_size = len(msg)
            times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / FREQ_SAMPLING
            voltage_mV = msg * VDD / VAL_MAX_ADC * 1e3

            plt.plot(times, voltage_mV)
            plt.title('Acquisition #{}'.format(msg_counter))
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.ylim([0,3300])
            plt.savefig("audio_files/Acquisition #{}.pdf".format(msg_counter), format="pdf")
            #plt.draw()
            #plt.pause(0.001)
            plt.clf()
            
            
            generate_audio(msg, 'acq-{}'.format(msg_counter))
            
#             #if args.fourier:
#             # Effectuez la transformation de Fourier
#             freqs = np.fft.fftfreq(buffer_size, 1 / FREQ_SAMPLING)
#             fft_values = np.fft.fft(msg)
#             
#             # Calculez la magnitude du spectre
#             magnitude = np.abs(fft_values)
#             
#             # Trouvez les fréquences positives (la moitié du spectre)
#             positive_freqs = freqs[:buffer_size // 2]
#             magnitude = magnitude[:buffer_size // 2]
#             
#             # Tracer le graphique de la transformée de Fourier
#             plt.plot(positive_freqs, magnitude)
#             plt.title('FFT of Acquisition #{}'.format(msg_counter))
#             plt.yscale('log')
#             #plt.xscale('log')
#             plt.xlabel('Frequency (Hz)')
#             plt.ylabel('Magnitude')
#             plt.grid()
#             plt.savefig("audio_files/Acquisition #{} Fourier.pdf".format(msg_counter), format="pdf")
#             #plt.show()
#             plt.clf()
            msg_counter+=1
            
            
            print("")
            print("Data save in audio_files")
            print("")



                
