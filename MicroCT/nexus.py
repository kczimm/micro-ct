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
            self.controller.view.toggleCTButtonText(self.controller.scanning)
        data_acq.close()
        drive2_comm.close()

class ScanStepWedgeThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        logging.debug('Scan button pressed')


        # Establish COM connection
        data_acq = serial.Serial('COM9')
        drive2_comm = serial.Serial(5)

        # Bislide model E01
        InchPerSec = 0.25
        ZStepPerIn = 4000
        WAIT_AFTER_WRITE = 0.08
        num_steps = self.controller.view.numSteps.get()
        dZ = 0.6

        while data_acq.read(data_acq.inWaiting()) != 'G': pass
        # Already in position
        data_acq.write('R')

        for i in range(1,num_steps):
            # Wait for complete token (G) (0x47)
            while data_acq.read(data_acq.inWaiting()) != 'G': pass
            if not self.controller.scanning:
                # Send stop to other computer
                data_acq.write('Q') # prematurely terminate the scanning.
                break
            # translate
            translate = ZStepPerIn*dZ
            drive2_cmd = 'F,C,I1M{0},R'.format(translate)
            drive2_comm.write(drive2_cmd)
            # Wait for rotate complete, time depends on d_theta
            time.sleep(dZ/InchPerSec)
            # Send acquisition token (R) (0x52)
            data_acq.write('R')
            # REPEAT

        # Translate back
        #translate = int(ZStepPerIn*dZ*i)
        #drive2_cmd = 'F,C,I1M{0},R'.format(-translate)
        #drive2_comm.write(drive2_cmd)
        # Wait for translation complete, time depends on distance
        #time.sleep(dZ/InchPerSec*num_steps)
        
        if self.controller.scanning:
            self.controller.scanning = False
            self.controller.view.toggleStepWedgeButtonText(self.controller.scanning)
        data_acq.close()
        drive2_comm.close()


class NexusController():
    def __init__(self,parent):
        self.parent = parent
        self.view = NexusView(self)
        self.scanning = False
    
    def scanCTButtonPressed(self):
        logging.debug('Scan button pressed')
        
        if not self.scanning:
          self.scanning = True
          thread = ScanThread(self)
          self.view.toggleCTButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.togglCTButtonText(self.scanning)
    def scanStepWedgeButtonPressed(self):
        logging.debug('Scan Step Wedge button pressed.')

        if not self.scanning:
          self.scanning = True
          thread = ScanStepWedgeThread(self)
          self.view.toggleStepWedgeButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.toggleStepWedgeButtonText(self.scanning)


class NexusView(Frame):
    def __init__(self,controller):
        self.frame = Toplevel(controller.parent)

        revision = 2.0
        
        self.frame.title('Nexus {0}'.format(revision))
        self.controller = controller
        
        self.frameRates = [0.2, 0.5, 1., 1.5, 2., 3., 3.75, 5., 6., 7.5, 10.]
        
        self.numViewsValue = IntVar()
        self.deltaThetaValue = DoubleVar()
        self.timePerViewValue = DoubleVar()
        self.numSteps = IntVar()
        
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
        self.scanCTButton = Button(self.frame,text='Scan',command=self.controller.scanCTButtonPressed,bg='green')
        self.scanCTButton.grid(row=4,column=0,columnspan=3,sticky=E+W)
        Label(self.frame,text='No. of Steps:').grid(row=5,column=0,stick=E)
        Spinbox(self.frame,textvariable=self.numSteps,from_=1,to=25,increment=1).grid(row=5,column=1)
        Label(self.frame,text='#').grid(row=5,column=2)
        self.scanStepWedgeButton = Button(self.frame,text='Scan Step Wedge Phantom',command=self.controller.scanStepWedgeButtonPressed,bg='yellow')
        self.scanStepWedgeButton.grid(row=6,column=0,columnspan=3,sticky=E+W)

    def toggleCTButtonText(self,scanning):
        if scanning:
            self.scanCTButton['text'] = 'Stop Scanning'
            self.scanCTButton['bg'] = 'red'
            self.scanStepWedgeButton['state'] = 'disabled'
        else:
            self.scanCTButton['text'] = 'Scan'
            self.scanCTButton['bg'] = 'green'
            self.scanStepWedgeButton['state'] = 'normal'
    def toggleStepWedgeButtonText(self,scanning):
        if scanning:
            self.scanStepWedgeButton['text'] = 'Stop Scanning'
            self.scanStepWedgeButton['bg'] = 'red'
            self.scanCTButton['state'] = 'disabled'
        else:
            self.scanStepWedgeButton['text'] = 'Scan Step Wedge Phantom'
            self.scanStepWedgeButton['bg'] = 'yellow'
            self.scanCTButton['state'] = 'normal'
