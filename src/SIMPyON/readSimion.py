#%%
import pandas as pd
import numpy as np

folder = '/home/cs268225/Documents/Work/CNRS/VMI/Models/Jansen/'
filename = 'geometry.csv'
df = pd.read_csv(folder+filename,skiprows=6)

# %%


start = df[::2]
splash = df[1::2]

####### STARTING CONDITIONS ##########
pos_R = np.sqrt(np.array(start['Y'])**2+np.array(start['Z'])**2)
pos_X = np.sqrt(np.array(start['Y'])**2+np.array(start['Z'])**2)

velocity_R = np.sqrt(np.array(start['Vy'])**2+np.array(start['Vz'])**2)
velociy_X =np.array(start['Vx'])

####### END CONDITIONS ##########
detec_time = np.array(splash['TOF']) #Time of arrival
detec_radius = np.sqrt(np.array(splash['Y'])**2+np.array(splash['Z'])**2)




