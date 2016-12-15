import os
import time
import shutil


from Tkinter import *
from ttk import Combobox
import tkFileDialog
import logging

import threading

import velmex

class ScanThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        d_theta = self.controller.view.deltaThetaValue.get()
        number_of_views = self.controller.view.numViewsValue.get()

        basename = self.controller.filename

        data_directory = 'C:\Users\Operator1\Desktop\provided-SW\LV2011_exe-SW\data'
        labview_filenames = os.path.join(data_directory,'data_{:>2}.dat')
        output_template = '{}{{}}.txt'.format(basename)

        number_of_files = 20

        file_numbers = range(0,number_of_files,2)

        for view_number in range(number_of_views):
            file_number = file_numbers[view_number % len(file_numbers)]
            labview_filename = os.path.abspath(labview_filenames.format(file_number))
            start_of_waiting = time.time()
            while os.path.getmtime(labview_filename) < start_of_waiting:
                continue
            time.sleep(1)
            shutil.copyfile(labview_filename, output_template.format(view_number))
            with velmex.Velmex() as motors:
                motors.rotate(d_theta, relative=True)
            if not self.controller.scanning:
                break

        if self.controller.scanning:
            self.controller.scanning = False
            self.controller.view.toggleButtonText(self.controller.scanning)

class ScanStepWedgeThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        steps = self.controller.view.stepsValue.get()

        basename = self.controller.filename

        data_directory = 'C:\Users\Operator1\Desktop\provided-SW\LV2011_exe-SW\data'
        labview_filenames = os.path.join(data_directory,'data_{:>2}.dat')
        output_template = '{}{{}}.txt'.format(basename)

        number_of_files = 20

        file_numbers = range(0,number_of_files,2)

        for step in range(steps):
            file_number = file_numbers[step % len(file_numbers)]
            labview_filename = os.path.abspath(labview_filenames.format(file_number))
            start_of_waiting = time.time()
            while os.path.getmtime(labview_filename) < start_of_waiting:
                continue
            time.sleep(1)
            shutil.copyfile(labview_filename, output_template.format(step))
            with velmex.Velmex() as motors:
                motors.translate_z(1.0, relative=True)
            if not self.controller.scanning:
                break

        if self.controller.scanning:
            self.controller.scanning = False
            self.controller.view.toggleStepWedgeButtonText(self.controller.scanning)


class DxRayController():
    def __init__(self,parent):
        self.parent = parent
        self.view = DxRayView(self)
        self.scanning = False

    def scanButtonPressed(self):
        logging.debug('Scan button pressed')

        if not self.scanning:
          self.filename = tkFileDialog.asksaveasfilename()
          if not self.filename:
            return
          self.scanning = True
          thread = ScanThread(self)
          self.view.toggleButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.toggleButtonText(self.scanning)

    def scanStepWedgeButtonPressed(self):
        logging.debug('Scan Step Wedge button pressed')

        if not self.scanning:
          self.filename = tkFileDialog.asksaveasfilename()
          if not self.filename:
            return
          self.scanning = True
          thread = ScanStepWedgeThread(self)
          self.view.toggleStepWedgeButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.toggleStepWedgeButtonText(self.scanning)


class DxRayView(Frame):
    def __init__(self,controller):
        self.frame = Toplevel(controller.parent);

        revision = 1.0

        self.frame.title('DxRay {0}'.format(revision))
        self.controller = controller

        self.numViewsValue = IntVar()
        self.deltaThetaValue = DoubleVar()

        self.stepsValue = IntVar()

        self.loadView()

    def loadView(self):
        Label(self.frame,text='No. of Views:').grid(row=0,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.numViewsValue,from_=0,to=720,increment=1).grid(row=0,column=1)
        Label(self.frame,text='#').grid(row=0,column=2)
        Label(self.frame,text='Angle between Views:').grid(row=1,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.deltaThetaValue,from_=0.0,to=90.0,increment=0.1).grid(row=1,column=1)
        Label(self.frame,text='deg').grid(row=1,column=2)
        self.scanButton = Button(self.frame,text='Scan',command=self.controller.scanButtonPressed,bg='green')
        self.scanButton.grid(row=2,column=0,columnspan=3,sticky=E+W)

        Label(self.frame,text='Steps:').grid(row=3,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.stepsValue,from_=1,to=40,increment=1).grid(row=3,column=1)
        Label(self.frame,text='#').grid(row=3,column=2)
        self.scanStepWedgeButton = Button(self.frame,text='Scan Step Wedge',command=self.controller.scanStepWedgeButtonPressed,bg='yellow')
        self.scanStepWedgeButton.grid(row=4,column=0,columnspan=3,sticky=E+W)

    def toggleButtonText(self,scanning):
        if scanning:
            self.scanButton['text'] = 'Stop Scanning'
            self.scanButton['bg'] = 'red'
            self.scanStepWedgeButton['state'] = 'disabled'
        else:
            self.scanButton['text'] = 'Scan'
            self.scanButton['bg'] = 'green'
            self.scanStepWedgeButton['state'] = 'normal'

    def toggleStepWedgeButtonText(self,scanning):
        if scanning:
            self.scanStepWedgeButton['text'] = 'Stop Scanning'
            self.scanStepWedgeButton['bg'] = 'red'
            self.scanButton['state'] = 'disabled'
        else:
            self.scanStepWedgeButton['text'] = 'Scan Step Wedge'
            self.scanStepWedgeButton['bg'] = 'yellow'
            self.scanButton['state'] = 'normal'
