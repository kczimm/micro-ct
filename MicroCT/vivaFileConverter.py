import Tkinter, tkFileDialog
import os
import struct
import tkMessageBox

class VivaFileConverter(Tkinter.Tk):
  def __init__(self, parent):
    Tkinter.Tk.__init__(self,parent)
    self.parent = parent
    self.setup()

  def setup(self):
    self.geometry('{}x{}'.format(300,80))
   
    label = Tkinter.Label(self,text='Directory:')
    label.grid(row=0,column=0)
   
    self.theDir = Tkinter.StringVar()
    self.dirEntry = Tkinter.Entry(self,textvariable=self.theDir)
    self.dirEntry.grid(column=1,row=0,sticky='EW')

    button = Tkinter.Button(self,text=u"Find",command=self.OnFindButtonClick)
    button.grid(column=2,row=0) 

    convert = Tkinter.Button(self,text=u"Convert",command=self.OnConvertButtonClick)
    convert.grid(row=1,column=0,columnspan=3)

  def OnFindButtonClick(self):
    theDir = tkFileDialog.askdirectory()
    if theDir:
      self.theDir.set(theDir)

  def OnConvertButtonClick(self):
    try:
      if self.theDir.get():
        for filename in os.listdir(self.theDir.get()):
          if filename.endswith('.raw'):
            self.convert(self.theDir.get(), filename)
    except OSError:
      pass

  def convert(self,path,filename):
    with open(os.path.join(path,filename),'rb') as f:
      rawData = f.read()

    rawsize = len(rawData)
    if rawsize == 1920*1536*2:
      width = 1536
      height = 1920
    elif rawsize == 768*960*2:
      width = 768
      height = 960
    else:
      return
    header = ["CSTv1.00",0,1,width,height,0,0,0,60,60+rawsize,5,1,0,16,0.0,0.0,0.0,0.0,0.0,0.0]
    formats = ['B','B','H','H','H','f','I','I','I','B','B','B','B','f','f','f','f','f','f']
    print len(header),len(formats)
    filename = ''.join([filename.strip('.raw'),'.cst'])
    with open(os.path.join(path,filename),'wb') as f:
      f.write(header[0])
      for i in range(0,len(formats)):
        f.write(struct.pack(formats[i],header[i+1]))
      f.write(rawData)

if __name__ == '__main__':
  version = 1.0
  converter = VivaFileConverter(None)
  converter.title('Viva File Converter v%1.1f' % version)
  converter.mainloop()
