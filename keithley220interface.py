# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 09:40:59 2022

@author: BRasmussen

ben.f.rasmussen@gmail.com

keithley 220 programmable current source interface
"""

import tkinter as tk
import keithley220 as k220
from tkinter import END

# correct port for device
k220port = 'GPIB12::12::INSTR'


# %% Checks for usb inputs and creates reource manager:

#   rm = pyvisa.ResourceManager('C:\Windows\System32\\visa64.dll')
#   reslist = rm.list_resources(query='?*')

# %%


# General instance of keithley class used within the interface:

instrument = k220.Keithley220(k220port)


class Interface(tk.Tk):
    '''
    Code to produce a fully interactible interface for the Keithley 220 current
    source. The master frame for Tkinter is called as a Tkinter object and 
    used as the object for this class. Much of the first code controls the 
    layout of the interface while the section on helper functions calls the
    Keithley220 python module directly. 

    '''

    def __init__(self):
        super().__init__()

        # configures base window
        self.title("Keithley 220 Programming Interface")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=2)
        self.grid_columnconfigure(5, weight=1)

        # makes different frames for visually relevant sections

        frame1 = tk.Frame(self, bd=5)
        frame1.grid(row=0, column=4, rowspan=8,
                    padx=5, pady=5, ipadx=5, ipady=5, sticky='n')
        frame1['relief'] = 'ridge'

        # frame to add in a current pulse generator control

        #frame2 = tk.Frame(self, bd=10, height=50, width=200)
       # frame2.grid(row=6, column=1, columnspan=4, sticky='w', pady=10, padx=5)
        #frame2['relief'] = 'groove'

        # TODO: add current pulse generator control

        # trigger and terminate buttons:
        self.btn_trigger = tk.Button(
            self, text='  Trigger   ', height=4, width=8, bg="#DAF5D6", activeforeground='green')
        self.btn_trigger["command"] = self.trigger_button_clicked
        self.btn_trigger.grid(row=2, column=1, columnspan=1, padx=5)
        self.btn_terminate = tk.Button(
            self, text="Terminate", height=4, width=8, bg="#F5D6D6", activeforeground='red')
        self.btn_terminate["command"] = self.terminate_button_clicked
        self.btn_terminate['state'] = 'disabled'
        self.btn_terminate.grid(row=2, column=2, padx=5, pady=10)

        # write to memory location button:
        self.btn_memory = tk.Button(
            self, text='Write to Memory', bg="#e1e0e0", height=2, activeforeground='white')
        self.btn_memory["command"] = self.write_to_memory_clicked
        self.btn_memory.grid(row=5, column=5, columnspan=1, padx=5)

        # program control and polarity reversal buttons:
        self.btn_reverse = tk.Button(
            self, text='  Reverse \n  polarity   ', height=4, width=8, bg="#DAD6F5", activeforeground='white')
        self.btn_reverse["command"] = self.reverse_polarity_clicked
        self.btn_reverse.grid(row=2, column=3, columnspan=1)
        self.btn_reverse['state'] = 'normal'

        self.btn_program_on = tk.Button(
            self, text='ON', height=1, width=2, bg="#DAF5D6", activeforeground='green')
        self.btn_program_on['command'] = self.program_on_helper
        self.btn_program_on.grid(row=5, column=1, sticky='w', padx=5)

        self.btn_program_off = tk.Button(
            self, text='OFF', height=1, width=2, bg="#F5D6D6", activeforeground='red')
        self.btn_program_off['command'] = self.program_off_helper
        self.btn_program_off.grid(row=5, column=1, sticky='e', padx=5)
        self.btn_program_off['state'] = 'disabled'

        self.program_label = tk.Label(self, text='Program Control Buttons')
        self.program_label.grid(row=5, column=2, columnspan=2, sticky='w')

        # Move to memory button and input:
        self.btn_move_to = tk.Button(
            self, text='*', height=20, width=60, bitmap='info', bg="#e1e0e0", activeforeground='red')

        self.btn_move_to["command"] = self.move_to_clicked
        self.btn_move_to.grid(row=3, column=1, pady=5)

        # display parameter entries:
        self.current_label = tk.Label(frame1, text='Current (A)')
        self.current_label.grid(row=2, column=4)
        self.current_entry = tk.Entry(frame1)
        self.current_entry.insert(-1, '0.0e-9')
        self.current_entry.grid(row=3, column=4)

        self.vlimit_label = tk.Label(frame1, text='Voltage Limit (V)')
        self.vlimit_label.grid(row=4, column=4)
        self.vlimit_entry = tk.Entry(frame1)
        self.vlimit_entry.insert(-1, '1')
        self.vlimit_entry.grid(row=5, column=4)

        self.dwell_time_label = tk.Label(frame1, text='Dwell Time (s)')
        self.dwell_time_label.grid(row=6, column=4)
        self.dwell_time_entry = tk.Entry(frame1)
        self.dwell_time_entry.insert(-1, '3e-3')
        self.dwell_time_entry.grid(row=7, column=4)

        self.buffer_label = tk.Label(frame1, text='Memory Location')
        self.buffer_label.grid(row=8, column=4)
        self.buffer_entry = tk.Entry(frame1)
        self.buffer_entry.insert(-1, '001')
        self.buffer_entry.grid(row=9, column=4)

        self.move_to_label = tk.Label(self, text='Location to Move to:')
        self.move_to_label.grid(row=3, column=2)
        self.move_to_entry = tk.Entry(self, width=5)
        self.move_to_entry.insert(-1, '001')
        self.move_to_entry.grid(row=3, column=3)

        # dropdown for program modes:

        self.program_mode_label = tk.Label(self, text='Program Mode Dropdown')
        self.program_mode_label.grid(row=4, column=2, columnspan=2, sticky='w')
        mode = tk.StringVar(self)
        mode.set("step")  # default value
        self.program_mode = tk.OptionMenu(
            self, mode, "step", "cont.", "single", command=self.program_mode_clicked)
        self.program_mode.config(height=1, width=4, bg="#e1e0e0")
        self.program_mode.grid(row=4, column=1)

        # trying to add customizable +/- x A button:

        # button

        self.btn_add_current = tk.Button(
            self, text='+', height=2, width=2, bg="#DAF5D6", activeforeground='cyan')
        self.btn_add_current.grid(row=2, column=5, sticky='w', padx=5)
        self.btn_add_current['command'] = self.add_value_to_current

        self.add_value = tk.StringVar(self)
        self.add_value.set('1 \u03BCA')  # default value
        self.step_size_add = tk.OptionMenu(
            self, self.add_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_add.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_add.grid(row=2, column=5, sticky='e', padx=5)

        self.btn_subtract_current = tk.Button(
            self, text='-', height=2, width=2, bg="#F5D6D6", activeforeground='cyan')
        self.btn_subtract_current.grid(row=3, column=5, sticky='w', padx=5)
        self.btn_subtract_current['command'] = self.subtract_value_from_current

        self.subtract_value = tk.StringVar(self)
        self.subtract_value.set('1 \u03BCA')  # default value
        self.step_size_subtract = tk.OptionMenu(
            self, self.subtract_value, "1 nA", "10 nA", "100 nA", "1 \u03BCA",
            "10 \u03BCA", "100 \u03BCA", "1 mA", "10 mA")
        self.step_size_subtract.config(height=2, width=5, bg="#e1e0e0")
        self.step_size_subtract.grid(row=3, column=5, sticky='e', padx=5)

        # TODO: make it with bind function or updating prior to trigger

    # %% Helper functions:

    def trigger_button_clicked(self):
        self.current_entry_pressed()
        self.vlimit_entry_pressed()
        self.dwell_time_entry_pressed()
        self.btn_trigger['state'] = 'disabled'
        self.btn_terminate['state'] = 'active'
        instrument.initialize_current()

    def terminate_button_clicked(self):
        self.btn_trigger['state'] = 'active'
        self.btn_terminate['state'] = 'disabled'
        instrument.terminate_current()

    def reverse_polarity_clicked(self):
        B = float(self.move_to_entry.get())
        instrument.reverse_polarity(B)

    def move_to_pressed(self):
        L = float(self.move_to_entry.get())
        instrument.moveto_memory(L)

    def move_to_clicked(self):
        self.move_to_pressed()

    def current_entry_pressed(self):
        B = float(self.buffer_entry.get())
        current = float(self.current_entry.get())
        instrument.set_current(current, B)

    def vlimit_entry_pressed(self):
        B = float(self.buffer_entry.get())
        vlimit = float(self.vlimit_entry.get())
        instrument.set_vlimit(vlimit, B)

    def dwell_time_entry_pressed(self):
        B = float(self.buffer_entry.get())
        dwell_time = float(self.dwell_time_entry.get())
        instrument.set_dwell_time(dwell_time, B)

    def write_to_memory_clicked(self):
        self.current_entry_pressed()
        self.vlimit_entry_pressed()
        self.dwell_time_entry_pressed()

    def program_mode_clicked(self, mode):

        if mode == "cont.":
            mode2 = 'continuous'
            instrument.set_program_mode(mode2)
        else:
            instrument.set_program_mode(mode)

    def program_on_helper(self):
        self.btn_program_on['state'] = 'disabled'
        self.btn_program_off['state'] = 'active'
        instrument.trigger()

    def program_off_helper(self):
        self.btn_program_on['state'] = 'active'
        self.btn_program_off['state'] = 'disabled'
        instrument.kill()

    def add_value_to_current(self):
        step_size = self.add_value.get()
        old = float(self.current_entry.get())
        new = 0
        if step_size == "1 nA":
            new = old + 1e-9
        elif step_size == "10 nA":
            new = old + 1e-8
        elif step_size == "100 nA":
            new = old + 1e-7
        elif step_size == "1 \u03BCA":
            new = old + 1e-6
        elif step_size == "10 \u03BCA":
            new = old + 1e-5
        elif step_size == "100 \u03BCA":
            new = old + 1e-4
        elif step_size == "1 mA":
            new = old + 1e-3
        elif step_size == "10 mA":
            new = old + 1e-2
        else:
            print('something\'s wrong, I can feel it')
        self.current_entry.delete(0, END)
        self.current_entry.insert(-1, "{:.9g}".format(new))
        instrument.set_current(new)

    def subtract_value_from_current(self):
        step_size = self.subtract_value.get()
        old = float(self.current_entry.get())

        # TODO: make it so the addition/subtraction occurs at desired location

        #location = float(self.buffer_entry.get())
        #data = instrument.get_data(location)
        #old = data[0]

        new = 0
        if step_size == "1 nA":
            new = old - 1e-9
        elif step_size == "10 nA":
            new = old - 1e-8
        elif step_size == "100 nA":
            new = old - 1e-7
        elif step_size == "1 \u03BCA":
            new = old - 1e-6
        elif step_size == "10 \u03BCA":
            new = old - 1e-5
        elif step_size == "100 \u03BCA":
            new = old - 1e-4
        elif step_size == "1 mA":
            new = old - 1e-3
        elif step_size == "10 mA":
            new = old - 1e-2
        else:
            print('something\'s wrong, I can feel it')
        self.current_entry.delete(0, END)
        print("{:.9g}".format(new))

        self.current_entry.insert(-1, "{:.9g}".format(new))
        instrument.set_current(new)

    # %%
if __name__ == "__main__":

    interface220 = Interface()

    interface220.mainloop()
