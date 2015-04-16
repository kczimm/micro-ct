from Tkinter import *
from ttk import Combobox
import tkFileDialog
import logging
import time
import serial

import threading

class ScanThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        logging.debug('Scan button pressed')


        # Establish COM connection
        data_acq = serial.Serial('COM9')
        drive2_comm = serial.Serial(5)

        RotateStepPerDeg = 80
        WAIT_AFTER_WRITE = 0.08
        DegPerSec = 12.5
        
        d_theta = self.controller.view.deltaThetaValue.get()
        num_views = self.controller.view.numViewsValue.get()
        for i in range(0,num_views):
            # Wait for complete token (G) (0x47)
            while data_acq.read(data_acq.inWaiting()) != 'G': pass
            if not self.controller.scanning:
                # Send stop to other computer
                data_acq.write('Q') # prematurely terminate the scanning.
                break
            # Rotate d_theta
            rotate = int(d_theta*RotateStepPerDeg)
            drive2_cmd = 'F,C,I2M{0},R'.format(rotate)
            drive2_comm.write(drive2_cmd)
            # Wait for rotate complete, time depends on d_theta
            time.sleep(d_theta/DegPerSec)
            # Send acquisition token (R) (0x52)
            data_acq.write('R')
            # REPEAT

        if self.controller.scanning:
            self.controller.scanning = False
            self.controller.view.toggleButtonText(self.controller.scanning)
        data_acq.close()
        drive2_comm.close()


class NexusController():
    def __init__(self,parent):
        self.parent = parent
        self.view = NexusView(self)
        self.scanning = False
    
    def scanButtonPressed(self):
        logging.debug('Scan button pressed')
        
        if not self.scanning:
          self.scanning = True
          thread = ScanThread(self)
          self.view.toggleButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.toggleButtonText(self.scanning)


class NexusView(Frame):
    def __init__(self,controller):
        self.frame = Toplevel(controller.parent);
        self.controller = controller
        
        self.frameRates = [0.2, 0.5, 1., 1.5, 2., 3., 3.75, 5., 6., 7.5, 10.]
        
        self.numViewsValue = IntVar()
        self.deltaThetaValue = DoubleVar()
        self.timePerViewValue = DoubleVar()
        
        self.loadView()
    
    def loadView(self):
        Label(self.frame,text='No. of Views:').grid(row=0,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.numViewsValue,from_=0,to=720,increment=1).grid(row=0,column=1)
        Label(self.frame,text='#').grid(row=0,column=2)
        Label(self.frame,text='Angle between Views:').grid(row=1,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.deltaThetaValue,from_=0.0,to=90.0,increment=0.1).grid(row=1,column=1)
        Label(self.frame,text='deg').grid(row=1,column=2)
        Label(self.frame,text='FPS:').grid(row=2,column=0,sticky=E)
        Label(self.frame,text='Time Per View:').grid(row=2,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.timePerViewValue,from_=0.001,to=60.000,increment=0.1).grid(row=2,column=1)
        Label(self.frame,text='s/view').grid(row=2,column=2)
        self.scanButton = Button(self.frame,text='Scan',command=self.controller.scanButtonPressed,bg='green')
        self.scanButton.grid(row=4,column=0,columnspan=3,sticky=E+W)

    def toggleButtonText(self,scanning):
        if scanning:
            self.scanButton['text'] = 'Stop Scanning'
            self.scanButton['bg'] = 'red'
        else:
            self.scanButton['text'] = 'Scan'
            self.scanButton['bg'] = 'green'
