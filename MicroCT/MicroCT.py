from Tkinter import *
import tkMessageBox
import logging

import varian
import nexus
import velmex
#import mfx

class MainController():
    def __init__(self,parent):
        self.parent = parent
        self.view = MainView(self)

    def nexusButtonPressed(self):
        logging.debug('Nexus button pressed')
        nexusApp = nexus.NexusController(self.parent)

    def varianButtonPressed(self):
        logging.debug('Varian button pressed.')
        varianApp = varian.VarianController(self.parent)

    def velmexButtonPressed(self):
        logging.debug('Velmex button pressed.')
        velmexApp = velmex.VelmexController(self.parent)

    def mfxButtonPressed(self):
        logging.debug('Microfocus X-ray button pressed.')
        #mfxApp = mfx.MFXController(self.parent)

class MainView(Frame):
    def __init__(self,controller):
        self.controller = controller
        self.frame = Frame();
        self.controller.parent.geometry('{}x{}'.format(260, 140))
        self.frame.grid(row=0,column=0)

        self.padx = 5
        self.pady = 5

        self.loadView()

        tkMessageBox.showwarning("REMINDER", "Warm up source before continuing.")
    def loadView(self):
        
        ## Detector section
        detectorLabel = Label(self.frame,text='Detectors').grid(row=0,column=0,pady=self.pady,padx=self.padx)
        varianButton = Button(self.frame,text='Varian Panel',command=self.controller.varianButtonPressed).grid(row=1,column=0,pady=self.pady,padx=self.padx)
        nexusButton = Button(self.frame,text='Nexus PCXD',command=self.controller.nexusButtonPressed).grid(row=2,column=0,pady=self.pady,padx=self.padx)

        ## Stage section
        stageLabel = Label(self.frame,text='Stage').grid(row=0,column=1,pady=self.pady,padx=self.padx)
        velmexButton = Button(self.frame,text='Velmex',command=self.controller.velmexButtonPressed).grid(row=1,column=1,pady=self.pady,padx=self.padx)

        ## Source section
        sourceLabel = Label(self.frame,text='Source').grid(row=0,column=2,pady=self.pady,padx=self.padx)
        mfxButton = Button(self.frame,text='Microfocus X-ray',command=self.controller.mfxButtonPressed).grid(row=1,column=2,pady=self.pady,padx=self.padx)

def main():
    logging.basicConfig(level=logging.CRITICAL)
    revision = 2.0
    root = Tk()
    root.title('MicroCT {0}'.format(revision))
    app = MainController(root)
    root.mainloop()

if __name__ == '__main__':
    main()
