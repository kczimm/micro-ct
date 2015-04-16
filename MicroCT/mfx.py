

class MFXModel():
    
    def __init__(self,controller):
        self.controller = controller
        self.voltage_value = IntVar()
        self.current_value = IntVar()
        self.focal_spot_size_value = StringVar()
        
        self.focal_spots = ['Large','Medium','Small']
        self.LARGE = 0
        self.MEDIUM = 1
        self.SMALL = 2
    
        self.readParameters()
    
    def readParameters(self):
        self.voltage_value.set(120)
        self.current_value.set(100)
        self.focal_spot_size_value.set(self.focal_spots[self.SMALL])

    def xrayOn(self):
        logging.debug('Turning X-ray on')
        pass

    def xrayOff(self):
        logging.debug('Turning X-ray off')
        pass

    def setVoltage(self,voltage_value):
        self.voltage_value.set(voltage_value)

    def setCurrent(self,current_value):
        self.current_value.set(current_value)

    def setFocalSpotSize(self,focal_spot_size_value):
        self.focal_spot_size_value.set(focal_spot_size_value)

    def getVoltage(self):
        return self.voltage_value.get()
    
    def getCurrent(self):
        return self.current_value.get()
    
    def getFocalSpotSize(self):
        return self.focal_spot_size_value.get()
