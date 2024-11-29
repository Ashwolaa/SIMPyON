import os
import pathlib
import matplotlib.pyplot as plt
import subprocess
import time
import pandas as pd
import numpy as np

class electrode():
    def __init__(self,index,locate=[0,0,0],scale=1) -> None:        
        self.index = index # Potential index
        self.scale = scale # Scaling of electrodes
        self.locate = locate # Position of electrodes
    def makeLocate(self,):
        return f'locate{self.locate[0],self.locate[1],self.locate[2],self.scale}'+'{'
    def makeElectrode(self,type,*args):
        # Reproduce the syntax expected to position an electrode, location + scale, then create electrode
        command = ''
        elec = f'e({self.index})'
        command+=elec+'{\n\t'        
        command+= self.makeLocate()        
        command+='\n\t\tfill{\n\t\t\twithin{\n\t\t\t\t'
        if type ==0: # CYLINDRICAL ELECTRODE
            command += self.makeCylindricalElectrode(*args)
        elif type==1:# POLYGONAL ELECTRODE
            command += self.makeCustomElectrode(*args)
        command+='\n\t}'
        return command
    def makeCylindricalElectrode(self,x_pos,rad_pos):
        #Return array for cylindrical electrode with a hole
        x_start = x_pos[0]
        x_end = x_pos[-1]
        r_start = rad_pos[0]
        r_end = rad_pos[-1]
        box = f'box2d({x_start},{r_start},{x_end},{r_end})'
        return box+'\n\t\t\t\t}\n\t\t\t}\n\t\t}'
    def makeCustomElectrode(self,edges):
        #Return array for polygone electrodes, each set of (x,y) represent a corner
        if len(edges)>4:
            box=f'polyline({edges})'
            return box+'}}}'        
        else:
            print('Not enough data points')


class SIMION():    

    def writeGemFile(filename,nx,ny,electrodeList,locate=[0,0,0],scale=1,):
        # Create a gem file from list of electrodes
        with open(f'{filename}','w+') as f:
            pa_definition = f'pa_define({nx},{ny},1, cylindrical, electrostatic)'            
            f.writelines(pa_definition)
            f.writelines('\n')
            f.writelines(f'locate{locate[0],locate[1],locate[2],scale}'+'{')
            f.writelines('\n')
            for e in electrodeList:
                f.writelines(e)
                f.writelines('\n')            
            f.writelines('}')
                            
    def simionCommand(command,command_type=None):        
        # General simion command for other scripts
        simon_exe = 'wine /media/cs268225/053b6b58-bb5a-4826-870f-304319eb9a60/constant/Documents/Simion/simion-8.0.5.exe' # Replace by your own .exe
        command = simon_exe + ' ' + command
        print(f'  {command_type}  '.center(140, '*'))
        print(f'Launching command:')
        print(command)
        print('\n')        
    
        try:
            start = time.time()
            os.system(command)                     
            print(f'Success, it took {(time.time()-start)}s')

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def gem2pa(gem_file=None,pa_file= None):                
        # Convert a gem file into a pa file
        if gem_file:
            P = pathlib.PurePath(gem_file)
            command = f' gem2pa {gem_file} '
            if not pa_file:                
                pa_file = str(P.with_suffix('.pa#'))
            command+=pa_file
            SIMION.simionCommand(command,command_type='Creating potential array')            
            return pa_file
                                    
    def refine(pa_file=None):
        # Refine a pa file
        if pa_file:
            P = pathlib.PurePath(pa_file)
            command = f' refine {pa_file} '            
            SIMION.simionCommand(command,command_type='Refining potential array')
            return pa_file
                
    def fastadj(pa_file,voltage_list=None):    
        "Fast adjust a pa0 file"
        P = pathlib.PurePath(pa_file)    
        if voltage_list:          
            command = ' fastadj '  
            command+=str(P.with_suffix('.pa0'))
            command+=' '        
            for i,v in enumerate(voltage_list):
                command+=f'{i+1}={v}'
                if (i+1) != len(voltage_list):
                    command+=','        
            SIMION.simionCommand(command,command_type='Fast adjusting voltages')

    def fly(iob_file=None,particle_file=None,recording_file=None,output_file=None,noPrompt=False):
        "Run a custom fly and record it"
        command = ''
        if noPrompt:
            command += '--noprompt --nogui '
        command += 'fly '        
        if particle_file:
            command+=f'--particle={particle_file} '
        if recording_file:
            command+=f'--recording={recording_file} '
        if iob_file:
            # command += "--adjustable scale = 1 --restore-potentials=0 --recording-enable=1 --recording-output=" in simion 8.1
            
            # restore-potentials=0 is to use pa0 specifically allowing to just adjust volage from fastadj function
            command += "--restore-potentials=0 --recording-enable=1 --recording-output=" 
            if output_file:
                command+= f'{output_file}'
            else:
                P = pathlib.PurePath(iob_file)    
                command+=str(P.with_suffix('.csv'))
            command+=f' {iob_file}'
            SIMION.simionCommand(command,command_type='Flying particles')
            
    def readFile(output_file=None):
        "Read File and return starting/end conditions "
        if output_file:            
            df = pd.read_csv(output_file,skiprows=6)
            start = df[::2] # Starting conditions
            splash = df[1::2] # Detector splash
            
            ####### STARTING CONDITIONS ##########
            # X is the ToF axis here
            pos_R = np.sqrt(np.array(start['Y'])**2+np.array(start['Z'])**2)
            pos_X = np.sqrt(np.array(start['Y'])**2+np.array(start['Z'])**2)
            vel_R = np.sqrt(np.array(start['Vy'])**2+np.array(start['Vz'])**2)
            vel_X =np.array(start['Vx'])
            
            ####### END CONDITIONS ##########
            detec_time = np.array(splash['TOF']) #Time of arrival
            detec_radius = np.sqrt(np.array(splash['Y'])**2+np.array(splash['Z'])**2)
            start_cond = {'posR': pos_R,'pos_X': pos_X,'vel_R': vel_R,'vel_X': vel_X,}
            end_cond = {'ToF': detec_time,'R': detec_radius}
            return start_cond,end_cond




#Workben in mm
origin=np.array([352,0,0]) # in mm
size_x,size_y = np.array([1000,200]) # in mm
scaling = 1 # in gu/mm
#Going to grid units
nx = size_x*scaling # in gu
ny = size_y*scaling # in gu
origin*=scaling # in gu


#Creating gem File

### JANSEN VMI ####
e = [electrode(0,[7.5,0,0],1).makeElectrode(0,[0,2],[7.5,15]),
     electrode(1,[27.5,0,0],1).makeElectrode(0,[0,2],[10,20]),
     electrode(2,[57.5,0,0],1).makeElectrode(0,[0,2],[15,30]),
     electrode(3,[-9.5,0,0],1).makeElectrode(0,[0,2],[10,20]),
     electrode(4,[-29.5,0,0],1).makeElectrode(0,[0,2],[15,30]),
     electrode(5,[-59.5,0,0],1).makeElectrode(0,[0,2],[20,40]),]

SIMION.writeGemFile('/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/a.gem',nx,ny,e,origin,scaling)
# ### PARKER VMI ####

# e = [electrode(0,[0,0,0],1).makeElectrode(0,[0,1],[1,35]),
#      electrode(1,[0,0,0],1).makeElectrode(0,[15,16],[10,35]),
#      electrode(2,[0,0,0],1).makeElectrode(0,[30,31],[10,35]),
#      electrode(2,[0,0,0],1).makeElectrode(0,[00,500],[42,45]),]
# SIMION.writeGemFile('/home/cs268225/Documents/Work/CNRS/VMI/Models/Parker/geometry.gem',500,100,e,[20,0,0])


################################ RUN FILE##############
gem_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/a.gem'
iob_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/geometry.iob'
rec_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test.rec'
fly_file = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test.fly2'
output_file= '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/test1.csv'

# Create ge
pa_file = SIMION.gem2pa(gem_file=gem_file,)
SIMION.refine(pa_file=pa_file,)
SIMION.fastadj(pa_file=pa_file,voltage_list=[-1000,-770,0])
# SIMION.simionCommand('lua /home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/geometry.lua') # In simion 8.1
SIMION.fly(iob_file=iob_file,recording_file=rec_file,particle_file=fly_file,output_file=output_file)
SIMION.readFile(output_file)

