
import SIMION
from electrodes import PolyLineElectrode, CylindricalElectrode
import numpy as np


def filename(filename,project_folder_path=''):
    return project_folder_path+filename

simion_exe_path = 'D:\\Work\\Simion\\simion-8.0.5.exe'
project_folder_path = 'D:\\Work\\Python\\VMI\\Models\\'


#Workben in mm
origin= [352,0,0] # in mm
size_x,size_y = np.array([1000,200]) # in mm
scaling = 1 # in gu/mm
#Going to grid units
nx = size_x*scaling # in gu
ny = size_y*scaling # in gu
origin*=scaling # in gu


S = SIMION(simion_exe_path,project_folder_path)



e = [CylindricalElectrode(0,width=(0,2),radius=(7.5,15),locate=(7.5,0,0)),
CylindricalElectrode(1,width=(0,2),radius=(7.5,15),locate=(15,0,0))]



gemfile = filename('a2',project_folder_path)    

S.make_geometry_file(nx,ny,gemfile,e,origin=origin,scale=scaling)



pafile = S.gem2pa(filename('a2.gem',project_folder_path))

S.refine(pafile)

S.fastadj()

# ################################ RUN FILE##############
# gem_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/a.gem'
# iob_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/geometry.iob'
# rec_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test.rec'
# fly_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test.fly2'
# output_file= '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test1.csv'

# # Create ge
# # pa_file = SIMION.gem2pa(gem_file=gem_file,)
# SIMION.refine(pa_file=pa_file,)
# # SIMION.fastadj(pa_file=pa_file,voltage_list=[-1000,-770,0])
# # SIMION.simionCommand('lua /home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/geometry.lua') # In simion 8.1
# # SIMION.fly(iob_file=iob_file,recording_file=rec_file,particle_file=fly_file,output_file=output_file)
# # SIMION.readFile(output_file)



# SIMION(simion_exe_path)