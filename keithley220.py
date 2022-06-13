# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 11:23:48 2022

@author: BRasmussen

ben.f.rasmussen@gmail.com

Code to control and program the Keithley 220 Current Source
"""

# import packages and modules:

import pyvisa
import numpy as np
import time


# correct port for device
k220port = 'GPIB12::12::INSTR'

# Checks for usb inputs and creates reource manager:

#   rm = pyvisa.ResourceManager('C:\Windows\System32\\visa64.dll')
#   reslist = rm.list_resources(query='?*')


class Keithley220():

    def __init__(self,
                 port,
                 I=0.0e-9,
                 V=1,
                 W=3e-3,
                 L=1,
                 PM='step',
                 PC=False,
                 output=False):
        """
       Initializes the instrument with instrument GPIB port that can be found
       above. Default source parameters are set in above and can be modified as
       needed. Initial current output is set to 'False':

       ----------
       port : str
           The GPIB port address of the Keithley 220
       I : float,optional
           The set current output of the instrument [range: 0-101mA]
       V : int, optional
           The voltage limit set to the instrument, defaults to 1 V
           [range: 1-105v]
       W : float, optional
           The set dwell time for particular memory location, defaults to 3e-3
           [range: 3e-3-999.9s]
       L : int, optional
           The set memory address of a particular set of programmed parameters
           Defaults to loaction 1, [range: 1-100]
       PM : str, optional
           Program mode which instrument will run through. Defaults to 'step'
           mode. Can take values ['single', 'continuous', 'step']
       PC : boolean, optional
           Program control to initialize above program mode. Only works in
           'single' or 'continous' mode, defaults to FALSE
       output : boolean, optional
           Initializes current output, defaults to FALSE (or off)

       """
       # Opens the resource manager within the class and initializes the
       # instrument as keithley
        self.rm = pyvisa.ResourceManager('C:\Windows\System32\\visa64.dll')
        self.keithley = self.rm.open_resource(port)

       # Sets the read and write termination characters
        self.keithley.read_termination = '\n'
        self.keithley.write_termination = '\n'

       # Sets the default values for each parameter within the class
        self.moveto_memory(L)
        self.set_current(I)
        self.set_vlimit(V)
        self.set_dwell_time(W)
        self.set_program_mode(PM)
        self.terminate_current()

    def set_current(self, I, B=1):
        '''
        Sets the current current value, optional parameter B
        where B is the buffer memory location. Defaults to 1.
        '''
        if -0.101 <= I <= 0.101:  # Amps
            curr_command = 'I' + str(I) + 'B' + str(B) + \
                'X'  # I command: I+nnnn+X

            self.keithley.write(curr_command)

        else:
            raise ValueError("IDDOC error: enter current in range")

    def set_vlimit(self, V, B=1):
        '''
        Sets voltage limit value, optional parameter B
        where B is the buffer memory location. Defaults to 1.
        '''
        if 0 < V <= 105:  # Volts
            volt_command = 'V' + str(V) + 'B' + str(B) +\
                'X'    # voltage command: V+nnnn+X
            self.keithley.write(volt_command)
        else:
            raise ValueError("IDDOC error: enter voltage in range")

    def set_dwell_time(self, W, B=1):
        '''
        Sets dwell time for memory allocation, optional
        parameter B where B is the buffer memory loaction. Defaults to 1.
        '''
        if 3e-3 <= W <= 999.9:  # seconds
            dwell_command = 'W' + str(W) + 'B' + str(B) + \
                'X'     # DT command: W+nnnn+X
            self.keithley.write(dwell_command)
        else:
            raise ValueError("IDDOC error: enter dwell time in range")

    def moveto_memory(self, L):
        '''
        Moves the output settings and display to the desired memory location.
        Essentially changes the current memory location to the desired one.
        '''

        if 1 <= L <= 100:  # unitless integer
            mem_command = 'L' + str(L) + 'X'  # memory command: L+nnn+X
            self.keithley.write(mem_command)
        else:
            raise ValueError("IDDOC error: enter memory location in range")

    def initialize_current(self, output=True):
        '''
        Starts output current by changing the operate function from FALSE
        To TRUE.
        '''
        if type(output) == bool:
            operate = '1'
            operate_command = 'F' + operate + 'X'    # op command: F+1+X
            self.keithley.write(operate_command)
        else:
            raise ValueError("Inappropriate argument value of type BOOL")

    def terminate_current(self, output=False):
        '''
        Terminates operational output by changing operate function from
        any state to FALSE
        '''

        if type(output) == bool:
            operate = 'O'
            operate_command = 'F' + operate + 'X'    # op command: F+1+X
            self.keithley.write(operate_command)
        else:
            raise ValueError("Inappropriate argument value of type BOOL")

    def set_program_mode(self, mode='step'):
        '''
        Sets particular program mode for desired output. Can take three
        different values:

        'single' : runs through all programmed memory locations once
        'continuous' : runs through memory locations continuously
        'step' : moves through discrete memory locations via user input
        '''

        if mode == 'single':
            mode_command = 'P0X'
            self.keithley.write(mode_command)
        elif mode == 'continuous':
            mode_command = 'P1X'
            self.keithley.write(mode_command)
        elif mode == 'step':
            mode_command = 'P2X'
            self.keithley.write(mode_command)
        else:
            raise ValueError("IDDC error: not valid program mode of" +
                             "type in list: ['single', 'continuous', 'step']")

    def get_data(self, mem_location):
        '''
        Gets the data from all four input locations for a desired memory 
        location

        Parameters
        ----------
        mem_location : int
            location of memory wanted

        Returns
        -------
        I_now : float
            current at mem_location
        V_now : float
            Voltage limit at mem_location
        W_now : float
            Dwell time at mem_location
        L_now : float
            memory loaction at mem_location

        '''
        self.moveto_memory(mem_location)
        current_data = self.keithley.query('*IDN?')
        current_data_list = current_data.split(',')

        # current data: kind of hacked together, must be better way to
        # split strings
        I_now = float(current_data_list[0][4:14])
        V_now = float(current_data_list[1][2:11])
        W_now = float(current_data_list[2][2:11])
        L_now = float(current_data_list[3][2:11])

        return [I_now, V_now, W_now, L_now]

    def reverse_polarity(self, mem_location=1):
        '''
        Reverses the polarity of the current flowing from the output

        Parameters
        ----------
        mem_location : int, optional
            memory loaction with which the polarity should be reversed

        Returns
        -------
        None.

        '''
        data = self.get_data(mem_location)
        current = data[0] * -1
        reverse_command = 'I' + str(current) + 'B' + str(mem_location) + 'X'
        self.keithley.write(reverse_command)
        self.keithley.write(reverse_command)

    # Optional methods to create different desired waveforms:

    def make_ramp_wave(self, I_range, dwell_time=0.1, points=100):
        '''
        Makes a programmed current output ramp wave with completely
        adjustable parameters. May take some time to run. 


        Parameters
        ----------
        I_range : 2 x 1 list/tuple
            lower and upper bounds on desired wave amplitude
        dwell_time : float, optional
            Time spent in each memory address. Defaults to 0.1. The length of 
            a wave pulse will be dwell_time * points
        points : integer, optional
            Amount of total memory addresses accessed by method.
            Defaults to every address with points = 100.

        Returns
        -------
        None.

        '''

        step_size = (I_range[1] - I_range[0]) / points

        for i in range(1, points+1):
            ramp_current = step_size * i
            self.set_current(ramp_current, i)
            self.set_dwell_time(dwell_time, i)
        self.set_program_mode('continuous')

    def make_sine_wave(self, amplitude, period, points=100):
        '''
        Makes a programmed current output sine wave with adjustable parameters.
        May take some time to run.

        Parameters
        ----------
        amplitude : float
            maximum current magnitude of the wave
        period : float
            time it takes to run through the n point sine wave
        points : int, optional
            amount of included memory positions. defaults to 100

        Returns
        -------
        None.

        '''
        dwell_time = period/points

        for i in range(1, points+1):
            ramp_current = amplitude * np.sin(np.pi * (2/points) * i)
            self.set_current(ramp_current, i)
            self.set_dwell_time(dwell_time, i)
        self.set_program_mode('continuous')

    def make_square_wave(self, amplitude, pause, pulse, PM='single'):
        '''
        Makes a programmed current ouput square wave or current pulse with
        adjustable parameters. Must reset other memory locations before use.

        TODO: use other memory locations or reset internally

        Parameters
        ----------
        amplitude : float
            height of current pulse
        pause : float
            length of pause before or between pulses
        pulse : float
            length of pulse duration

        Returns
        -------
        None.

        '''

        if PM == 'continuous':
            self.set_current(0, 1)
            self.set_current(amplitude, 2)
            self.set_dwell_time(pause, 1)
            self.set_dwell_time(pulse, 2)

            self.set_program_mode(PM)

        elif PM == 'single':
            self.set_current(0, 1)
            self.set_current(amplitude, 2)
            self.set_current(0, 3)
            self.set_dwell_time(pause/2, 1)
            self.set_dwell_time(pulse, 2)
            self.set_dwell_time(pause/2, 3)

            self.set_program_mode(PM)

    def make_arbitrary_waveform(self, I_max, period, points=100):
        '''
        Makes arbitrary waveform using an in-class written mathematical 
        function that is normalized to the inputted max value.

        Parameters
        ----------
        I_max : float
            maximum current value of the waveform
        period : float
            length of one cycle of the waveform
        points : int, optional
            number of memory locations acccessed by waveform, defaults to 100

        Returns
        -------
        None.

        '''

        dwell_time = period/points

        point_eval = np.linspace(0, 1, points)  # function only in range [0,1]

        # ENTER DESIRED FUNCTION HERE: must be continuous in interval
        waveform = (np.sin(40*point_eval - 5)) / (40*point_eval-5)
        #############################

        # normalizes to the desired max current
        max_val = max(waveform)
        norm_to_max_waveform = (waveform / max_val) * I_max

        for i in range(1, points+1):
            self.set_current(norm_to_max_waveform[i-1], i)
            self.set_dwell_time(dwell_time, i)

        self.set_program_mode('continuous')

    # Methods designed to trigger and terminate the operation of the keithley:

    def trigger(self):
        '''
        In program modes 'single' and 'continuous' this method will trigger
        the operation of the programmed waveform 

        Returns
        -------
        None.

        '''
        self.keithley.write('T4X')

    def kill(self):
        '''
        In program modes 'single' and 'continous' this method will kill
        any operating program

        Returns
        -------
        None.

        '''
        self.keithley.write('T5X')

# makes keithley object for testing

#keith = Keithley220(k220port, -0.0767, 7, 6)
