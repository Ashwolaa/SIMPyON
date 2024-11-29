import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def readFile(output_file=None):
        "Read File and return starting/end conditions "
        if output_file:            
            df = pd.read_csv(output_file,skiprows=6,)

            # Slicing to choose between starting/splash/crossing
            start = df[::2] # Starting conditions
            splash = df[1::2] # Detector splash
            
            ####### STARTING CONDITIONS ##########
            # X is the ToF axis here
            pos_R = np.sqrt(np.array(start['Y'])**2+np.array(start['Z'])**2)
            pos_X = np.array(start['X'])
            vel_R = np.sqrt(np.array(start['Vy'])**2+np.array(start['Vz'])**2)
            vel_X = np.array(start['Vx'])
            
            ####### END CONDITIONS ##########
            detec_time = np.array(splash['TOF']) #Time of arrival
            detec_radius = np.sqrt(np.array(splash['Y'])**2+np.array(splash['Z'])**2)
            start_cond = {'posR': pos_R,'pos_X': pos_X,'vel_R': vel_R,'vel_X': vel_X,} #Dictionary syntax
            end_cond = {'ToF': detec_time,'R': detec_radius} 
            return df


folder = 'C:\\Users\\constant.schouder\\Desktop\\'
filename = 'test.csv'

df = readFile(output_file=folder+filename,)

a = 0
