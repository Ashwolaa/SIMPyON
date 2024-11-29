from SIMPyON.filenames import Filenames
import subprocess
import time
import numpy as np
import os
import SIMPyON.electrodes

class SIMION_PA():
    """SIMION_PA class to setup PA workbench."""

    def __init__(self, origin=np.array([0,0,0],dtype=float),size= np.array([10,10],dtype=int),scaling=1,filename=''):
        """"""                
        self.origin = origin
        self.nx,self.ny = size
        self.scaling = scaling
        self.filename =filename
    
    def Nx(self,):
        return int(self.nx*self.scaling)
    
    def Ny(self,):
        return int(self.ny*self.scaling)
    
    def origin_gu(self,):
        return self.origin*self.scaling    
            
    @property
    def origin(self,):
        return self._origin

    @origin.setter
    def origin(self,origin):
        if type(origin)==int:
            origin = np.concatenate([[origin],[0,0]])
        elif type(origin) is np.ndarray:
            if len(origin)==1:
                origin = np.concatenate([origin,[0,0]])
            elif len(origin)==2:
                origin = np.concatenate([origin,[0]])
        self._origin= origin    
        
    @property
    def nx(self):
        """str: get the title of the module"""
        return self._nx
    @nx.setter
    def nx(self, N:int):
        self._nx = N
    @property
    def ny(self):
        """str: get the title of the module"""
        return self._ny
    @ny.setter
    def ny(self, N:int):
        self._ny = N
        
    @property
    def scaling(self):
        """str: get the title of the module"""
        return self._scaling
    @scaling.setter
    def scaling(self, scaling:float):
        self._scaling = scaling

    @property
    def scaling(self):
        """str: get the title of the module"""
        return self._scaling
    @scaling.setter
    def scaling(self, scaling:float):
        self._scaling = scaling

    @property
    def filename(self):
        """str: get the title of the module"""
        return self._filename
    @filename.setter
    def filename(self, filename:str):
        if not filename.endswith('.gem'):
            filename = filename+'.gem'    
        self._filename = filename
   
    def make_gem(self, input_list:list,):
        pa_define_string = f'pa_define({self.Nx()},{self.Ny()},{1},cylindrical,{''},electrostatic)'
        with open(self.filename, 'w') as f:
            f.write(f'; {''}\n') # header
            f.write(pa_define_string + '\n\n') # pa_define

            x, y, z = self.origin_gu()
            f.write(f'locate({x},{y},{z},{self.scaling}) ;position in grid units x,y,z,gu/mm\n') # scaling and origin
            f.write(f'{{\n') # scaling and origin
            for input in input_list:
                if issubclass(type(input),SIMPyON.electrodes.Element):
                    electrode_string = input.buildString()                
                    f.write(electrode_string)
                else:
                    f.write(f'include({input})')
                f.write('\n')
            f.write('}')
        print(f'Geometry file "{os.path.basename(self.filename)}" generated in working directory:\n{os.path.dirname(self.filename)}.')
        print(f'Workbench dimensions: nx = {self.Nx()}, ny = {self.Ny()}, nz = 1 (gu).')
        return self.filename



    def get_gem(self,filename=None):    
        if not filename:
            filename = self.filename    
        with open(filename, 'r') as f:
            strings = f.read()
            strings = strings.split('locate')[1:]
            strings = ['locate'+string for string in strings]
            elec = [SIMPyON.electrodes.makeElement(string) for string in strings]
        return elec


def main():
    print('Hello world!')

if __name__ == '__main__':
    main()
