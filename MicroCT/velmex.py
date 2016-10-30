from Tkinter import *
import logging
import serial
import time

class VelmexController():
    def __init__(self,parent):
        self.parent = parent
        self.view = VelmexView(self)
        self.model = VelmexModel(self)

        self.view.x_value.set(str(self.model.getXValue()))
        self.view.y_value.set(str(self.model.getYValue()))
        self.view.z_value.set(str(self.model.getZValue()))
        self.view.tilt_value.set(str(self.model.getTiltValue()))
        self.view.rotate_value.set(str(self.model.getRotateValue()))
        self.view.y2_value.set(str(self.model.getY2Value()))

    def move(self,*args):
        logging.debug('Move button pressed')
        self.model.setXValue(float(self.view.x_value.get()))
        self.model.setYValue(float(self.view.y_value.get()))
        self.model.setZValue(float(self.view.z_value.get()))
        self.model.setY2Value(float(self.view.y2_value.get()))
        self.model.setRotateValue(float(self.view.rotate_value.get()))
        self.model.setTiltValue(float(self.view.tilt_value.get()))
        self.model.sendPositions()
        self.model.readPositions()

class VelmexView(Frame):
    def __init__(self,controller):
        self.frame = Toplevel(controller.parent);

        revision = 1.2

        self.frame.title('Velmex {0}'.format(revision))
        self.controller = controller

        self.x_value = StringVar()
        self.y_value = StringVar()
        self.z_value = StringVar()
        self.y2_value = StringVar()
        self.tilt_value = StringVar()
        self.rotate_value = StringVar()

        self.loadView()

    def loadView(self):
        moveButton = Button(self.frame,text='Move',command=self.controller.move).grid(row=6,column=0,columnspan=7,sticky=E+W)
        stageLabel = Label(self.frame,text='Stage').grid(row=0,column=0,columnspan=3)
        detectorLabel = Label(self.frame,text='Detector').grid(row=0,column=4,columnspan=3)
        xLabel = Label(self.frame,text='X:').grid(row=1,column=0,sticky=E)
        xSpinbox = Spinbox(self.frame,textvariable=self.x_value,from_=-50.00,to=50.00,increment=0.01)
        xSpinbox.grid(row=1,column=1)
        xSpinbox.bind('<Return>', self.controller.move)
        xUnitLabel = Label(self.frame,text='cm').grid(row=1,column=2)
        yLabel = Label(self.frame,text='Y:').grid(row=2,column=0,sticky=E)
        ySpinbox = Spinbox(self.frame,textvariable=self.y_value,from_=0.00,to=50.00,increment=0.01)
        ySpinbox.grid(row=2,column=1)
        ySpinbox.bind('<Return>', self.controller.move)
        yUnitLabel = Label(self.frame,text='cm').grid(row=2,column=2)
        zLabel = Label(self.frame,text='Z:').grid(row=3,column=0,sticky=E)
        zSpinbox = Spinbox(self.frame,textvariable=self.z_value,from_=0.00,to=50.00,increment=0.01)
        zSpinbox.grid(row=3,column=1)
        zSpinbox.bind('<Return>', self.controller.move)
        zUnitLabel = Label(self.frame,text='cm').grid(row=3,column=2)
        tiltLabel = Label(self.frame,text='Tilt:').grid(row=4,column=0,sticky=E)
        tiltSpinbox = Spinbox(self.frame,textvariable=self.tilt_value,from_=0.00,to=90.00,increment=0.01)
        tiltSpinbox.grid(row=4,column=1)
        tiltSpinbox.bind('<Return>', self.controller.move)
        tiltUnitLabel = Label(self.frame,text='deg').grid(row=4,column=2)
        rotateLabel = Label(self.frame,text='Rotate:').grid(row=5,column=0,sticky=E)
        rotateSpinbox = Spinbox(self.frame,textvariable=self.rotate_value,from_=0.00,to=360.00,increment=0.01)
        rotateSpinbox.grid(row=5,column=1)
        rotateSpinbox.bind('<Return>', self.controller.move)
        rotateUnitLabel = Label(self.frame,text='deg').grid(row=5,column=2)
        y2Label = Label(self.frame,text='Y2:').grid(row=1,column=4,sticky=E)
        y2Spinbox = Spinbox(self.frame,textvariable=self.y2_value,from_=0.00,to=50.00,increment=0.01)
        y2Spinbox.grid(row=1,column=5)
        y2Spinbox.bind('<Return>', self.controller.move)
        y2UnitLabel = Label(self.frame,text='cm').grid(row=1,column=6)

class VelmexModel():

    def __init__(self,controller):
        self.controller = controller

        self.XStepPerIn = 4000
        self.YStepPerIn = 4000
        self.ZStepPerIn = 4000
        self.TiltStepPerDeg = 80
        self.RotateStepPerDeg = 80
        self.Y2StepPerIn = 4000

        self.CmPerIn = 2.54

        self.WAIT_AFTER_WRITE = 0.08

        self.x_value = DoubleVar()
        self.y_value = DoubleVar()
        self.z_value = DoubleVar()
        self.y2_value = DoubleVar()
        self.tilt_value = DoubleVar()
        self.rotate_value = DoubleVar()

        self.readPositions()

    def readPositions(self):
        # Use Serial to set all location values
        logging.debug('Getting positions over COM')

        factor = 100

        drive1_comm = serial.Serial(4)
        drive2_comm = serial.Serial(5)
        try:
            drive1_comm.write('F,X')
            time.sleep(self.WAIT_AFTER_WRITE)
            x_step = drive1_comm.read(drive1_comm.inWaiting())
            self.x_value.set(int(factor*float(x_step)/self.XStepPerIn*self.CmPerIn)/(1.*factor))

            drive1_comm.write('F,Z')
            time.sleep(self.WAIT_AFTER_WRITE)
            y_step = int(drive1_comm.read(drive1_comm.inWaiting()))
            self.y_value.set(int(factor*float(y_step)/self.YStepPerIn*self.CmPerIn)/(1.*factor))

            drive2_comm.write('F,X')
            time.sleep(self.WAIT_AFTER_WRITE)
            z_step = int(drive2_comm.read(drive2_comm.inWaiting()))
            self.z_value.set(int(factor*float(z_step)/self.ZStepPerIn*self.CmPerIn)/(1.*factor))

            drive1_comm.write('F,T')
            time.sleep(self.WAIT_AFTER_WRITE)
            y2_step = int(drive1_comm.read(drive1_comm.inWaiting()))
            self.y2_value.set(int(factor*float(y2_step)/self.Y2StepPerIn*self.CmPerIn)/(1.*factor))

            drive1_comm.write('F,Y')
            time.sleep(self.WAIT_AFTER_WRITE)
            tilt_step = int(drive1_comm.read(drive1_comm.inWaiting()))
            self.tilt_value.set(int(factor*float(tilt_step)/self.TiltStepPerDeg)/(1.*factor))

            drive2_comm.write('F,Y')
            time.sleep(self.WAIT_AFTER_WRITE)
            rotate_step = int(drive2_comm.read(drive2_comm.inWaiting()))
            self.rotate_value.set(int(factor*float(rotate_step)/self.RotateStepPerDeg)/(1.*factor))
        except:
            pass


        drive1_comm.close()
        drive2_comm.close()

    def sendPositions(self):
        # Use Serial to send all location values
        logging.debug('Sending positions over COM')

        drive1_comm = serial.Serial(4)
        drive2_comm = serial.Serial(5)
        try:
            x = int(self.getXValue()*self.XStepPerIn/self.CmPerIn)
            y = int(self.getYValue()*self.YStepPerIn/self.CmPerIn)
            z = int(self.getZValue()*self.ZStepPerIn/self.CmPerIn)
            y2 = int(self.getY2Value()*self.Y2StepPerIn/self.CmPerIn)
            rotate = int(self.getRotateValue()*self.RotateStepPerDeg)
            tilt = int(self.getTiltValue()*self.TiltStepPerDeg)

            drive1_cmd = 'F,C,IA1M{0},IA2M{1},IA3M{2},IA4M{3},R'.format(x,tilt,y,y2)
            drive2_cmd = 'F,C,IA1M{0},IA2M{1},R'.format(z,rotate)

            drive1_comm.write(drive1_cmd)
            drive2_comm.write(drive2_cmd)

        except:
            pass


        drive1_comm.close()
        drive2_comm.close()

        self.readPositions()

    def getXValue(self):
        return self.x_value.get()

    def getYValue(self):
        return self.y_value.get()

    def getZValue(self):
        return self.z_value.get()

    def getTiltValue(self):
        return self.tilt_value.get()

    def getRotateValue(self):
        return self.rotate_value.get()

    def getY2Value(self):
        return self.y2_value.get()

    def setXValue(self,x_value):
        self.x_value.set(x_value)

    def setYValue(self,y_value):
        self.y_value.set(y_value)

    def setZValue(self,z_value):
        self.z_value.set(z_value)

    def setTiltValue(self,tilt_value):
        self.tilt_value.set(tilt_value)

    def setRotateValue(self,rotate_value):
        self.rotate_value.set(rotate_value)

    def setY2Value(self,y2_value):
        self.y2_value.set(y2_value)



class Velmex(object):

    DRIVE_COM_1 = 4
    DRIVE_COM_2 = 5

    X_STEPS_PER_IN = 4000
    Y_STEPS_PER_IN = 4000
    Z_STEPS_PER_IN = 4000
    TILT_STEPS_PER_DEG = 80
    ROTATE_STEPS_PER_DEG = 80
    Y2_STEPS_PER_IN = 4000

    CM_PER_IN = 2.54

    WAIT_AFTER_WRITE = 0.08

    X_MOVE_TEMPLATE = 'F,C,IA1M{},R'
    Y_MOVE_TEMPLATE = 'F,C,IA3M{},R'
    Z_MOVE_TEMPLATE = 'F,C,IA1M{},R'
    Y2_MOVE_TEMPLATE = 'F,C,IA4M{},R'
    ROTATE_TEMPLATE = 'F,C,IA2M{},R'
    TILT_TEMPLATE = 'F,C,IA2M{},R'

    X_DRIVE = 1
    Y_DRIVE = 1
    Z_DRIVE = 2
    Y2_DRIVE = 1
    ROTATE_DRIVE = 2
    TILT_DRIVE = 1

    def __init__(self):
        pass

    def __enter__(self):
        self.drive1 = serial.Serial(Velmex.DRIVE_COM_1)
        self.drive2 = serial.Serial(Velmex.DRIVE_COM_2)
        return self

    def __exit__(self, *args):
        self.drive1.close()
        self.drive2.close()

    def wait(self):
        time.sleep(Velmex.WAIT_AFTER_WRITE)

    def send_command(self, drive, command):
        if drive == 1:
            self.drive1.write(command)
        elif drive == 2:
            self.drive2.write(command)
        else:
            raise ValueError('Drive must be 1 or 2.')
        self.wait()

    def translate_x(self, x_cm):
        x_steps = int(x_cm/Velmex.CM_PER_IN*Velmex.X_STEPS_PER_IN)
        command = Velmex.X_MOVE_TEMPLATE.format(x_steps)
        self.send_command(Velmex.X_DRIVE, command)

    def translate_y(self, y_cm):
        y_steps = int(y_cm/Velmex.CM_PER_IN*Velmex.Y_STEPS_PER_IN)
        command = Velmex.Y_MOVE_TEMPLATE.format(y_steps)
        self.send_command(Velmex.Y_DRIVE, command)

    def translate_z(self, z_cm):
        z_steps = int(z_cm/Velmex.CM_PER_IN*Velmex.Z_STEPS_PER_IN)
        command = Velmex.Z_MOVE_TEMPLATE.format(z_steps)
        self.send_command(Velmex.Z_DRIVE, command)

    def translate_y2(self, y2_cm):
        y2_steps = int(y2_cm/Velmex.CM_PER_IN*Velmex.Y2_STEPS_PER_IN)
        command = Velmex.Y2_MOVE_TEMPLATE.format(y2_steps)
        self.send_command(Velmex.Y2_DRIVE, command)

    def rotate(self, deg):
        rotate_steps = int(deg*Velmex.ROTATE_STEPS_PER_DEG)
        command = Velmex.ROTATE_TEMPLATE.format(rotate_steps)
        self.send_command(Velmex.ROTATE_DRIVE, command)

    def tilt(self, deg):
        tilt_steps = int(deg*Velmex.TILT_STEPS_PER_DEG)
        command = Velmex.TILT_TEMPLATE.format(tilt_steps)
        self.send_command(Velmex.TILT_DRIVE, command)
