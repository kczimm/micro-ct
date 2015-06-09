from ctypes import *
from struct import *
import time

from Tkinter import *
from ttk import Combobox
import tkFileDialog
import logging
import serial

import threading

class ScanThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        OpenReceptorLink()

        COM5 = serial.Serial(5)

        RotateStepPerDeg = 80
        WAIT_AFTER_WRITE = 0.08
        DegPerSec = 12.5

        basename = self.controller.basename

        binning = self.controller.view.modes.index(self.controller.view.binningValue.get())
        gain = self.controller.view.gainValue.get()
        offset = self.controller.view.offsetValue.get()
        pixel = self.controller.view.pixelValue.get()
        
        dTheta = self.controller.view.deltaThetaValue.get()
        numViews = self.controller.view.numViewsValue.get()
        fps = self.controller.view.fpsValue.get()
        for i in range(0,numViews):
            angle = float(dTheta*i)
            filename = '%s%0.4d' % ( basename, i )
            PerformAcquisition(filename,fps,binning,gain,offset,pixel,angle)
            rotate = int(dTheta*RotateStepPerDeg)
            command = 'F,C,I2M{0},R'.format(rotate)
            COM5.write(command)
            time.sleep(dTheta/DegPerSec)  # For rotation time
            time.sleep(2) # For afterglow
            if not self.controller.scanning:
              break

        if self.controller.scanning:
            self.controller.scanning = False
            self.controller.view.toggleButtonText(self.controller.scanning)
        CloseReceptorLink()
        COM5.close()


class VarianController():
    def __init__(self,parent):
        self.parent = parent
        self.view = VarianView(self)
        self.scanning = False
    
    def scanButtonPressed(self):
        logging.debug('Scan button pressed')
        if not self.scanning:
          self.basename = tkFileDialog.asksaveasfilename()
          
          if self.basename == '': return
          self.scanning = True
          thread = ScanThread(self)
          self.view.toggleButtonText(self.scanning)
          self.view.frame.focus_set()
          thread.start()
        else:
          self.scanning = False
          self.view.toggleButtonText(self.scanning)


class VarianView(Frame):
    def __init__(self,controller):
        self.frame = Toplevel(controller.parent);

        revision = 1.4
        
        self.frame.title('Varian {0}'.format(revision))
        self.controller = controller
        
        self.frameRates = [0.2, 0.5, 1., 1.5, 2., 3., 3.75, 5., 6., 7.5, 10.]
        self.modes = ['2x2 0.5pF VG1','1x1 0.5pF VG1']
        
        self.numViewsValue = IntVar()
        self.deltaThetaValue = DoubleVar()
        self.fpsValue = DoubleVar()
        self.binningValue = StringVar()
        self.gainValue = IntVar()
        self.offsetValue = IntVar()
        self.pixelValue = IntVar()

        self.gainValue.set(1)
        self.offsetValue.set(1)
        self.pixelValue.set(1)
        
        self.loadView()
    
    def loadView(self):
        Label(self.frame,text='No. of Views:').grid(row=0,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.numViewsValue,from_=0,to=720,increment=1).grid(row=0,column=1)
        Label(self.frame,text='#').grid(row=0,column=2)
        Label(self.frame,text='Angle between Views:').grid(row=1,column=0,sticky=E)
        Spinbox(self.frame,textvariable=self.deltaThetaValue,from_=0.0,to=90.0,increment=0.1).grid(row=1,column=1)
        Label(self.frame,text='deg').grid(row=1,column=2)
        Label(self.frame,text='FPS:').grid(row=2,column=0,sticky=E)
        Spinbox(self.frame,values=[str(x) for x in self.frameRates],textvariable=self.fpsValue).grid(row=2,column=1)
        Label(self.frame,text='frames/s').grid(row=2,column=2)
        Label(self.frame,text='Mode:').grid(row=3,column=0,sticky=E)
        box = Combobox(self.frame,textvariable=self.binningValue,values=self.modes)
        box.current(1)
        box.grid(row=3,column=1)
        Checkbutton(self.frame,text='Offset Corrections',variable=self.offsetValue).grid(row=4,column=0,columnspan=3)
        Checkbutton(self.frame,text='Gain Corrections',variable=self.gainValue).grid(row=5,column=0,columnspan=3)
        Checkbutton(self.frame,text='Pixel Defect Map',variable=self.pixelValue).grid(row=6,column=0,columnspan=3)
        self.scanButton = Button(self.frame,text='Scan',command=self.controller.scanButtonPressed,bg='green')
        self.scanButton.grid(row=7,column=0,columnspan=3,sticky=E+W)

    def toggleButtonText(self,scanning):
        if scanning:
            self.scanButton['text'] = 'Stop Scanning'
            self.scanButton['bg'] = 'red'
        else:
            self.scanButton['text'] = 'Scan'
            self.scanButton['bg'] = 'green'


HCP_FLU_SEQ_PRMS = 3
HCP_DBG_OFF = 0
HCP_DBG_ON = 1
HCP_NO_ERR = 0

HCP_CORR_NONE = 0
HCP_CORR_STD = c_int(1)

VIP_NO_ERR = 0
VIP_SW_PREPARE = 0
VIP_SW_VALID_XRAYS = 1
VIP_SW_RADIATION_WARNING = 2
VIP_SW_RESET = 3
VIP_SW_FRAME_SUMMING = 4

RECORD_TIMEOUT = 100

WORD = c_ushort

MAX_STR = 256

FrameRates = [0.2, 0.5, 1., 1.5, 2., 3., 3.75, 5., 6., 7.5, 10.]

class SOpenReceptorLink(Structure):
  _fields_ = [("StructSize", c_int),
              ("VcpDatPtr", c_void_p),
              ("RecDirPath", c_char * MAX_STR),
              ("TestMode", c_int),
              ("DebugMode", c_int),
              ("RcptNum", c_int),
              ("MaxRcptCount", c_int),
              ("MaxModesPerRcpt", c_int),
              ("FgTargetPtr", c_void_p),
              ("BufferLen", c_int),
              ("SubModeBinX", c_int),
              ("SubModeBinY", c_int),
              ("TimeoutBoostSec", c_int),
              ("TimeoutBoostMsVcpCall", c_int),
              ("CallMutexOverride", c_bool),
              ("FgCallbackFlag", c_int),
              ("FgCallbackPtr", c_void_p),
              ("Reserved2", c_int),
              ("Reserved1", c_int)]

class SQueryProgInfo(Structure):
  _fields_ = [("StructSize", c_int),
              ("NumFrames",c_int),
              ("Complete",c_bool),
              ("NumPulses",c_int),
              ("ReadyForPulse",c_bool)]

class SSeqPrms(Structure):
  _fields_ = [("StructSize", c_int),
             ("NumBuffers", c_int),
             ("SeqX", c_int),
             ("SeqY", c_int),
             ("SumSize", c_int),
             ("SampleRate", c_int),
             ("BinFctr", c_int),
             ("StopAfterN", c_int),
             ("OfstX", c_int),
             ("OfstY", c_int),
             ("RqType", c_int),
             ("SnugMemory", c_int)]

class SAcqPrms(Structure):
  _fields_ = [("StructSize", c_int),
             ("StartUp", c_int),
             ("ReqType", c_int),
             ("CorrType", c_int),
             ("CorrFuncPtr", c_void_p),
             ("ThresholdSelect", c_void_p),
             ("CopyBegin", POINTER(c_double)),
             ("CopyEnd", POINTER(c_double)),
             ("ArraySize", c_int),
             ("MarkPixels", c_int),
             ("FrameErrorTolerance", c_int),
             ("LivePrmsPtr", c_void_p)]

class SCorrections(Structure):
  _fields_ = [("StructSize", c_int),
             ("Ofst", c_int),
             ("Gain", c_int),
             ("Dfct", c_int),
             ("Line", c_int),
             ("PixDataFormat", c_int),
             ("GainRatio", c_float),
             ("Rotate90", c_int),
             ("FlipX", c_int),
             ("FlipY", c_int),
             ("Reserved1", c_int)]

class SCorrectImage(Structure):
  _fields_ = [("StructSize", c_int),
             ("BufIn", POINTER(WORD)),
             ("BufInX", c_int),
             ("BufInY", c_int),
             ("BufOut", POINTER(WORD)),
             ("BufOutX", c_int),
             ("BufOutY", c_int),
             ("CorrType", c_int),
             ("Reserved1", c_int)]

def PerformOffsetCalibration():
  dll = CDLL("VirtCp.dll")

  GCrntStatus = SQueryProgInfo()
  
  dll.vip_reset_state()
  GSelectedMode = 0
  result = dll.vip_offset_cal(c_int(GSelectedMode))
  while result == HCP_NO_ERR and not GCrntStatus.Complete:
    result = QueryProgress()
  return result

def PerformGainCalibration():
  dll = CDLL("VirtCp.dll")
  GCrntStatus = SQueryProgInfo()
  
  mode = c_int(0)
  numCalFrmSet = c_int(0)
  result = dll.vip_get_num_cal_frames(mode, byref(numCalFrmSet))

  # tell the system to prepare for a gain calibration
  if result == VIP_NO_ERR:
    result = dll.vip_gain_cal_prepare(mode)
  # send prepare = true
  if result == VIP_NO_ERR:
    result = dll.vip_sw_handshaking(VIP_SW_PREPARE, c_bool(True))
  # wait for readyForPulse
  while True:
    result = QueryProgress()
    if result == HCP_NO_ERR and not GCrntStatus.ReadyForPulse:
      break
  # send xrays = true - this signals the START of the FLAT-FIELD ACQUISITION
  if result == VIP_NO_ERR:
    result = dll.vip_sw_handshaking(VIP_SW_VALID_XRAYS, c_bool(True))

  maxFrms = c_int(0)
  while True:
    result = QueryProgress()
    if maxFrms > GCrntStatus.NumFrames:
      break
    if result == HCP_NO_ERR and GCrntStatus.NumFrames < numCalFrmSet:
      break
  # wait for readyForPulse

  # TODO

  return result

def PerformAcquisition(filename, fps, binning, gain, offset, pixel, angle):
  if fps not in FrameRates:
    print fps
    return
  
  dll = CDLL("VirtCp.dll")

  #---STEP 1--- Set sequence information
  result = dll.vip_select_mode(c_int(binning))
  GNumFrames = 0
  numBuf = 1
  numFrm = numBuf
  
  seqPrms = SSeqPrms()
  seqPrms.StructSize = c_int(sizeof(SSeqPrms))
  seqPrms.NumBuffers = numBuf
  seqPrms.SeqX = 0
  seqPrms.SeqY = 0
  seqPrms.SumSize = 0
  seqPrms.SampleRate = 0
  seqPrms.BinFctr = 1
  seqPrms.StopAfterN = numFrm
  seqPrms.OfstX = 0
  seqPrms.OfstY = 0
  seqPrms.RqType = 0
  seqPrms.SnugMemory = 0
  
  result = dll.vip_fluoro_set_prms(HCP_FLU_SEQ_PRMS, byref(seqPrms))
  
  numBuf = seqPrms.NumBuffers
  if numFrm > numBuf: numFrm = numBuf

  result = dll.vip_set_frame_rate(c_int(binning),c_double(fps))
  if result != VIP_NO_ERR:
    return result

  #---STEP 2--- Start the grabber
  if result == VIP_NO_ERR:
    acqPrms = SAcqPrms()
    acqPrms.StructSize = c_int(sizeof(SAcqPrms))
    acqPrms.CorrType = HCP_CORR_STD
    acqPrms.CorrFuncPtr = None
    acqPrms.ReqType = 0

    corr = SCorrections()
    corr.StructSize = c_int(sizeof(SCorrections))
    corr.Ofst = c_int(offset)
    corr.Gain = c_int(gain)
    corr.Dfct = c_int(pixel)
    result = dll.vip_set_correction_settings(byref(corr))
    result = dll.vip_set_correction_settings(byref(corr))
    if result == HCP_NO_ERR:
      result = dll.vip_fluoro_grabber_start(byref(acqPrms))
    if result == HCP_NO_ERR:
      GGrabbingIsActive = True
  else:
    return result

  #---STEP 4--- Start recording
  if result == VIP_NO_ERR:
    result = dll.vip_fluoro_record_start(c_int(1),c_int(0))
  else:
    return result
  #---STEP 5--- End recording / STEP 6
  if result == VIP_NO_ERR:
    to = RECORD_TIMEOUT * 1000
    lpNum = 200
    qRate = to / lpNum * 1.0
    #time.sleep(qRate / 1000)
    result = dll.vip_fluoro_grabber_stop()
  else:
    return result
  #---STEP 7---
  if result == VIP_NO_ERR:
    if binning == 1:
      x_size = 1536
      y_size = 1920
    else:
      x_size = 768
      y_size = 960
    size = x_size*y_size
    buf = POINTER(WORD)()

    result = dll.vip_fluoro_get_buffer_ptr(byref(buf),c_int(0),c_int(1))

    corrImage = SCorrectImage()
    corrImage.StructSize = c_int(sizeof(SCorrectImage))
    corrImage.BufIn = buf
    corrImage.BufInX = x_size
    corrImage.BufInY = y_size
    corrImage.BufOut = buf
    corrImage.BufOutX = x_size
    corrImage.BufOutY = y_size
    corrImage.CorrType = c_int(0)

    result = dll.vip_correct_image(byref(corrImage))
    
    with open(''.join([filename, '.raw']), 'wb') as f:
      for i in xrange(0,size):
        f.write(pack('H',buf[i]))


    header = ["CSTv1.00",0,1,x_size,y_size,1,angle,0,60,60+size*2,4,1,0,16,-1.0,-1.0,-1.0,-1.0,0.0,1.0]
    formats = ['B','B','H','H','H','f','I','I','I','B','B','B','B','f','f','f','f','f','f']
    
    with open(''.join([filename, '.cstp']), 'wb') as f:
      f.write(header[0])
      for i in range(0,len(formats)):
        f.write(pack(formats[i],header[i+1]))
      for i in xrange(0,size):
        f.write(pack('H',buf[i]))
      
  else:
    return result

def QueryProgress():
  dll = CDLL("VirtCp.dll")
  HCP_U_QPI = 0
  prevStatus = SQueryProgInfo()
  prevStatus.StructSize = c_int(sizeof(SQueryProgInfo))
  prevStatus.numFrames = c_int(1)
  result = dll.vip_query_prog_info(HCP_U_QPI,byref(GCrntStatus))
  return result
  

def OpenReceptorLink():
  dll = CDLL("VirtCp.dll")
  orl = SOpenReceptorLink()
  orl.StructSize = c_int(sizeof(SOpenReceptorLink))
  orl.VcpDatPtr = None
  orl.RecDirPath = "C:\\IMAGERs\\234S01-0303"
  orl.TestMode = c_int(0)
  orl.DebugMode = c_int(HCP_DBG_ON)
  result = dll.vip_open_receptor_link(byref(orl))
  return result

def CloseReceptorLink():
  dll = CDLL("VirtCp.dll")
  result = dll.vip_close_link(c_int(1))
  return result
