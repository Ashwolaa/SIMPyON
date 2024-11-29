class Detector:
    def __init__(self,position=[0,0,0],energy_scaling:list = [0.0025,0,0],tof_scaling=0.25,label:str='') -> None:
        self.position=position
        self.energy_scaling=energy_scaling
        self.tof_scaling=tof_scaling
        self.label=label        

    @property
    def position(self):
        """str: get the title of the module"""
        return self._position
    
    @position.setter
    def position(self, position:float):
        self._position = position 

    @property
    def tof_scaling(self):
        """str: get the title of the module"""
        return self._tof_scaling
    @tof_scaling.setter
    def tof_scaling(self, tof_scaling:float):
        self._tof_scaling = tof_scaling

    @property
    def energy_scaling(self):
        """str: get the title of the module"""
        return self._energy_scaling
    @energy_scaling.setter
    def energy_scaling(self, energy_scaling:list or float):
        self._energy_scaling = energy_scaling

    @energy_scaling.setter
    def energy_scaling(self, energy_scaling:list or float):
        self._energy_scaling = energy_scaling

    @property
    def label(self):
        """str: get the title of the module"""
        return self._label
    @label.setter
    def label(self, label:bool):
        self._label = label
