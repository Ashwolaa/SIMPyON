import SIMPyON.utils.strings as s_utils
import os 
import numpy as np

def make_fly2_file(fly_filename: str, fly2_group:list) -> None:
        """ Creates a .fly2-file based on the given parameters """
        fly_file = open(fly_filename, 'w')
        fly_file.write('particles {\n')
        fly_file.write('\tcoordinates = 0,\n')
        for group in fly2_group:
            if type(group) == dict:
                fly_file.write(make_fly2_group(**group))        
            elif type(group) == list:
                 [fly_file.write(make_fly2_group(**gr)) for gr in group]                        
            elif type(group) == str:
                 fly_file.write(group)        

        fly_file.write('}')
        fly_file.close()
        return fly_filename

def make_fly2_group(
    n=100,mass=10,charge=1,kinetic_energy=2,
                    position = {'center':(0,0,0),'axis':(0,1,0),'radius':0.1,'length':3,'fill':True},direction = {'axis':(-1, 0, 0),'half_angle':180,'fill':True},**kwargs):
    strings = []
    strings.append('standard_beam {')              
    strings.append(f'n = {n},')
    strings.append(f'ke = {kinetic_energy},')
    strings.append(f'mass = {mass},')
    strings.append(f'charge = {charge},')
    strings.append(f'tob = {0},')
    for key in kwargs:
            strings.append(f'{key} = {kwargs[key]},')
    strings.append(make_pos(position))
    strings.append(make_dir(direction))        
    strings.append('},\n')              
    strings = s_utils.list_indent(strings,2)
    return '\n'.join(strings)
def make_pos(position):
    strings_in = f'position = cylinder_distribution \u007b\n'
    strings = []
    # strings.append(f'position = cylinder_distribution \u007b')
    strings.append(f'center = vector{position['center']},')
    strings.append(f'axis = vector{position['axis']},')
    strings.append(f'radius = {position['radius']},')                                 
    strings.append(f'length = {position['length']},')                                                                    
    strings.append(f'fill = {str(position['fill']).lower()},')                   
    strings.append('\u007d,')                          
    return strings_in+'\n'.join(s_utils.list_indent(strings,3))

def make_dir(direction):
    strings_in = f'direction = cone_direction_distribution \u007b\n'
    strings = []
    # strings.append(f'direction = cone_direction_distribution \u007b')
    strings.append(f'axis = vector{direction['axis']},')
    strings.append(f'half_angle = {direction['half_angle']},')                                                         
    strings.append(f'fill = {str(direction['fill']).lower()},')                                             
    strings.append('\u007d,')                          
    return strings_in+'\n'.join(s_utils.list_indent(strings,3))

def fly_particles(n_part=100,ke_list=[2,],mass=10,charge=1,center=(0,0,0),fly_list=[]):
    for i,ke in enumerate(ke_list):
        fly_dic = {'n':n_part,'mass':mass,'charge':charge,'kinetic_energy':ke,'position':{'center':(center),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(0, 1, 0),'half_angle':180,'fill':True},'cwf':1,
        'color':0,}          
        fly_list.append(fly_dic)
    return fly_list
        

# def fly_ions(mass=10,**kwargs):
#      return fly_particles(mass=mass,charge=1,**kwargs)
    # fly_list = []
    # filename = os.path.join(project_folder_path,f'test.fly2')
    # for i in np.arange(0,10,2):
    #     filename = os.path.join(project_folder_path,f'test{i}.fly2')
    #     # output_file = os.path.join(project_folder_path,'test{i}.csv')
    #     fly_dic_ion = {'n':1000,'mass':10,'charge':1,'kinetic_energy':i,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    #     'color':0,}  
    #     fly_list.append(fly_dic_ion)
    # for i in np.arange(0,10,2):
    #     # filename = os.path.join(project_folder_path,f'test{i}.fly2')
    #     # output_file = os.path.join(project_folder_path,'test{i}.csv')
    #     fly_dic_elect = {'n':1000,'mass':0.000548579903,'charge':-1,'kinetic_energy':i,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    #     'color':0,}  
    #     fly_list.append(fly_dic_elect)    
     
def fly_examples(filename,origin_mm=[0,0,0],n_part=100,doIons=True,doElectrons=True):
    fly_list = []
    if doIons:
        ke_list = np.array([0,1,2,4,6,8,])
        fly_list = fly_particles(n_part,ke_list,mass=100,charge=1,center=tuple(origin_mm),fly_list=fly_list)
    if doElectrons:
        ke_list = np.array([0,2,4,8,12,16,])
        fly_list = fly_particles(n_part,ke_list,mass=0.000548579903,charge=-1,center=tuple(origin_mm),fly_list=fly_list)
    filename = make_fly2_file(filename,fly_list)
    return filename

def main():
    print('Hello world!')
    project_folder_path = r'C:\Users\constant.schouder\Documents\Python\VMI\Models\Test'
    filename = os.path.join(project_folder_path,'test.fly2')
    fly_dic_ion = {'n':1000,'mass':10,'charge':1,'kinetic_energy':2,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    'color':0,}    
    fly_dic_elect = {'n':1000,'mass':0.000548579903,'charge':-1,'kinetic_energy':2,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    'color':0,}    
    # strings = make_fly2_group(**fly_dic)
    make_fly2_file(filename,[fly_dic_ion,fly_dic_elect])
if __name__ == '__main__':
    main()
