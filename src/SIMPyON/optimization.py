import scipy.optimize as opt       
import numpy as np
from SIMPyON.detector import Detector
from SIMPyON.SIMION_reader import SIMION_reader
from SIMPyON.SIMION import SIMION
import matplotlib.pyplot as plt
from scipy.optimize import Bounds

def costEnergyScaling(energy,splash,energy_scaling):
    return np.sum((energy - np.polyval(energy_scaling,splash))**2)

def costDetectorHit(hitPos,det_pos):
    return np.sum((hitPos-det_pos[0])**2)

def cost_func(cost,cost_scale):
    return cost*cost_scale

def make_voltage_list(factors,voltages_params,):
    voltage_change = voltages_params['starting_voltages'][voltages_params['isAdjustable']]*factors
    voltage_list = voltages_params['starting_voltages'].copy()
    voltage_list[voltages_params['isAdjustable']] = voltage_change
    voltage_list = voltage_list[voltages_params['isSame']]
    return voltage_list

def make_voltage_list2(factors,voltages_params,):
    # starting_voltages = np.array([300,500,-500,750,-1250])        
    voltage_list = voltages_params['starting_voltages'].copy()
    voltage_list = voltage_list*factors
    voltage_list = np.concatenate([[voltage_list[0],-voltage_list[0]],voltage_list[1:],voltage_list[-2::]])
    # voltage_change = voltages_params['starting_voltages'][voltages_params['isAdjustable']]*factors
    # voltage_list = voltages_params['starting_voltages'].copy()
    # voltage_list[voltages_params['isAdjustable']] = voltage_change
    # voltage_list = voltage_list[voltages_params['isSame']]
    return voltage_list

class Optimization():
    
    def __init__(self,simion_instance:SIMION,simion_reader:SIMION_reader,detectors:list) -> None:
        self.S = simion_instance
        self.R = simion_reader
        self.D = detectors

    # ================================================ Optimizer ============================================================
    def optimize_voltages(self,factors,voltages_params,):      
        cost = 0
        voltage_list = make_voltage_list2(factors,voltages_params,)
        # ========== adjust voltages ==========
        self.S.fastadj(pa_file=self.S.filenames.pa_file,voltages=voltage_list)
        # ========== flying ions ==========
        output_file = self.S.fly_no_input()
        # ========== read output ==========
        start,splash = self.R.loadFlighData(output_file)    
        # ========== loop for each detector ==========
        for i_c,charge in enumerate([1,-1]):
            mask = start['Charge']==charge        
            cost += self.calculate_cost(start[mask],splash[mask],self.D[i_c])
        # ========== return cost ==========
        return cost    
    # ================================================ Cost functions ============================================================
    def calculate_cost(self,start,splash,detector:Detector):
        cost = 0
        # ========== Detector hit ==========
        cost += cost_func(costDetectorHit(splash['X'],detector.position),cost_scale=1000)
        # ========== Energy scaling ==========
        cost += cost_func(costEnergyScaling(self.R.getRadialEnergy(start),self.R.getRadialPosition(splash),detector.energy_scaling),cost_scale=1)
        return cost

    def minimize(self,):
        # ================================================ Setup voltages ============================================================
        #Custom cylindrical
        starting_voltages = np.array([300,-300,500,-500,750,-1250,1250,-1250,])        
        isSame = np.array([0,1,2,3,4,5,6,7,6,7])
        isAdjustable = np.zeros_like(isSame,dtype=bool)
        isAdjustable = np.ones_like(isSame,dtype=bool)
        # isAdjustable[1::2] = True
        isAdjustable = np.unique(isSame[isAdjustable])
        starting_factors = np.ones_like(isAdjustable)


        starting_voltages = np.array([400,500,-500,750,-1250,1250,-1250])
        starting_factors = np.ones_like(starting_voltages)

        voltages_param = dict(starting_voltages=starting_voltages,isAdjustable=isAdjustable,isSame=isSame,)

        # ================================================ Setup bounds ============================================================
        lb,ub = np.zeros_like(starting_factors),np.ones_like(starting_factors)*np.inf
        bounds = Bounds(lb,ub)
        # ================================================ Setup optimizer ============================================================
        args =(voltages_param,)
        minimizer_kwargs = {'method':'Nelder-Mead', 'options':{'disp':True,'fatol':1,'maxiter':100}, 'args': args,'bounds':bounds,}
        self.result = opt.minimize(self.optimize_voltages, starting_factors, **minimizer_kwargs)
        return self.result




    # ================================================ Do plot ============================================================
    def plotResolution(self,):
        output_file = self.S.fly_no_input()
        # ========== read output ==========
        start,splash = self.R.loadFlighData(output_file)    
        # ========== loop for each detector ==========
        plt.figure()
        for i_c,charge in enumerate([1,-1]):
            mask = start['Charge']==charge        
            if sum(mask)>0:
                radE = self.R.getRadialEnergy(start[mask])
                r = self.R.getRadialPosition(splash[mask])
                cost = self.calculate_cost(start[mask],splash[mask],self.D[i_c])
                polyfit = np.polyfit(r,radE,2,full=True)    
                plt.plot(r,radE,'o',label=charge)
                plt.plot(r,np.polyval(polyfit[0],r),'o',label=f'Cost:{cost}')
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.legend()
        plt.show()



from zoopt import Dimension , Objective , Parameter , Opt , ExpOpt , Solution

class Optimization_zoopt():
    
    def __init__(self,simion_instance:SIMION,simion_reader:SIMION_reader,detectors:list) -> None:
        self.S = simion_instance
        self.R = simion_reader
        self.D = detectors
    # ================================================ Optimizer ============================================================
    def optimize_voltages(self,factors,voltages_params,):      
        cost = 0
        voltage_list = make_voltage_list(factors,voltages_params,)
        # ========== adjust voltages ==========
        self.S.fastadj(pa_file=self.S.filenames.pa_file,voltages=voltage_list)
        # ========== flying ions ==========
        output_file = self.S.fly_no_input()
        # ========== read output ==========
        start,splash = self.R.loadFlighData(output_file)    
        # ========== loop for each detector ==========
        for i_c,charge in enumerate([1,-1]):
            mask = start['Charge']==charge        
            cost += self.calculate_cost(start[mask],splash[mask],self.D[i_c])
        # ========== return cost ==========
        return cost    
    # ================================================ Cost functions ============================================================
    def calculate_cost(self,start,splash,detector:Detector):
        cost = 0
        # ========== Detector hit ==========
        cost += cost_func(costDetectorHit(splash['X'],detector.position),cost_scale=1000)
        # ========== Energy scaling ==========
        cost += cost_func(costEnergyScaling(self.R.getRadialEnergy(start),self.R.getRadialPosition(splash),detector.energy_scaling),cost_scale=1)
        return cost

    def minimize(self,):
        # ================================================ Setup voltages ============================================================
        #Custom cylindrical
        starting_voltages = np.array([300,-300,500,-500,750,-1250,1250,-1250,])
        isSame = np.array([0,1,2,3,4,5,6,7,6,7])
        isAdjustable = np.zeros_like(isSame,dtype=bool)
        isAdjustable[1::2] = True
        isAdjustable = np.unique(isSame[isAdjustable])
        starting_factors = np.ones_like(isAdjustable)
        voltages_param = dict(starting_voltages=starting_voltages,isAdjustable=isAdjustable,isSame=isSame,)
        # ================================================ Setup bounds ============================================================
        lb,ub = np.zeros_like(starting_factors),np.ones_like(starting_factors)*np.inf
        bounds = Bounds(lb,ub)
        # ================================================ Setup optimizer ============================================================
        args =(voltages_param,)
        minimizer_kwargs = {'method':'Nelder-Mead', 'options':{'disp':True,'fatol':500,'maxiter':100}, 'args': args,'bounds':bounds,}
        self.result = opt.minimize(self.optimize_voltages, starting_factors, **minimizer_kwargs)
        return self.result        
# calculate_cost

# dim = len ( init_volts )
# sol0 = Solution ( x= init_volts )
# param = Parameter ( budget =5000 , intermediate_result =True ,
# intermediate_freq =10 , init_samples =[ sol0 ])
# obj = Objective ( Metric , Dimension ( dim , bounds , [ True ]* dim ) )

# # start optimization and print optimized values
# start = time . time ()
# solution = Opt . min ( obj , param )
# end = time . time ()
# print ( end - start )



# class MyTakeStep:
#    def __init__(self, stepsize=0.5):
#        self.stepsize = stepsize
#        self.rng = np.random.default_rng()
#    def __call__(self, x):
#        s = self.stepsize
#        x[0] += self.rng.uniform(-2.*s, 2.*s)
#        x[1:] += self.rng.uniform(-s, s, x[1:].shape)
#        return x
# class step_fun:
#     """Step function for basin-hopping optimization"""
#     def __init__(self, stepsize, n_voltages, voltage_scale, offset_scale):
#         self.stepsize = stepsize
#         self.rng = np.random.default_rng()
#         self.n_voltages = n_voltages
#         self.voltage_scale = voltage_scale
#         self.offset_scale = offset_scale
#     def __call__(self, x): # __call__ method makes the instance callable
#         s = self.stepsize # maximum stepsize
#         # voltage step
#         x[:self.n_voltages] += self.rng.uniform(-self.voltage_scale*s, self.voltage_scale*s, 
#                                                 size=x[:self.n_voltages].shape) 
#         # geometry-parameter (offset) step
#         x[self.n_voltages:self.n_voltages+2] += self.rng.uniform(-self.offset_scale*s, self.offset_scale*s, 
#                                                                  size=x[self.n_voltages:self.n_voltages+2].shape) 
#         # geometry-parameter (coeff) step
#         x[self.n_voltages+2:] += self.rng.uniform(-s, s, size=x[self.n_voltages+2:].shape) 
#         return x



# # Define custom variable step size function
# def custom_variable_step(x):
#     # Define a variable step size based on the current value of x
#     step_size = x/20
#     return x+np.random.uniform(low=-step_size, high=step_size, size=x.shape)
# # Define custom accept_test function
# def custom_accept_test(f_new, f_old):
#     return f_new < f_old  # Accept the new solution if it's better
# def print_fun(x, f, accepted):
#         print("at minimum %.4f accepted %d" % (f, int(accepted)))


# def voltage_optimization(self, voltages: list[float], adjustable: list[bool], voltage_guess: list[float], fnames: Filenames, opt_type: str = 'VMI', prompt_result: bool = True) -> float:
#         """ Cost function for optimizing voltages for either VMI or SMI """
#         assert (opt_type == 'VMI') or (opt_type == 'SMI'), 'Optimization type should either be \'VMI\' or \'SMI\''

#         # First perform fast adjust
#         # voltages is only as long as the number of adjustable electrodes
#         # use voltage_guess to fast adjust - it has the right length, and we do not change the
#         # electrodes that should not be adjusted
#         count = 0
#         for i, voltage in enumerate(voltage_guess):
#             if adjustable[i]:
#                 voltage_guess[i] = voltages[count]
#                 count += 1

#         S.fastadj(fnames.iob_filename.removesuffix('.iob') + '.pa#', voltage_guess)

#         if prompt_result:
#             print(f'Voltages: {voltages} \n')

#         # Then fly ions
#         S.fly(fnames.iob_filename, fnames.fly_filename, fnames.rec_filename, fnames.output_filename,
#                  command_type='Flying ions: voltage optimization')
#         if self.operating_system == 'linux':
#             subprocess.call(['/bin/bash', '-c', 'rm *.tmp'])

#         # Then read out data and calculate cost
#         df_ic, df_res = R.load_flight_data(fnames.output_filename)
#         print(f'Output filename: {fnames.output_filename}')
#         # print(f'PA0 filename: {fnames.iob_filename.removesuffix('.iob') + '.pa0'}')

#         # Calculate the penalty (same velocity (vector!) must have same y-values) for VMI
#         # For SVMI we minimize the y-spread for same inital y-position
#         # Make sure that ions always hit the detector!
#         penalty = 0
#         initial_energies = df_ic['KE'].unique()
#         initial_azimuth = df_ic['Azm'].unique()
#         initial_elevation = df_ic['Elv'].unique()
#         initial_y = df_ic['Y'].unique()
#         if opt_type == 'VMI':
#             for energy in initial_energies:
#                 for aximuth in initial_azimuth: 
#                     for elevation in initial_elevation:
#                         mask = (df_ic['KE'] == energy) & (df_ic['Azm'] == aximuth) & (df_ic['Elv'] == elevation)
#                         y_pos = df_res.loc[mask]['Y']
#                         if  y_pos.empty:
#                             break
#                         penalty += (y_pos.max() - y_pos.min())**2 
#             for x in df_res['X']:
#                 penalty += 3000*(x - 542.5 - 27.5)**2  
#             for y in df_res['Y']:
#                 penalty += 1000 if y < 0 else 0
#                 penalty += 1000 if y > 20 else 0

#         elif opt_type == 'SMI':
#             for init_y in initial_y:
#                 y_pos = df_res[df_ic['Y'] == init_y]['Y']
#                 if y_pos.empty:
#                     break
#                 penalty += (y_pos.max() - y_pos.min())**2

#         else:
#             print('How\'d ya get here?')

#         # Keep descending voltage order
#         for i in range(len(voltages) - 2): # Minus two due to lens!
#             if voltages[i+1] > voltages[i]:
#                 penalty += 500

#         if prompt_result:
#             print('The penalty for this runs is: ', penalty, '\n')
        
#         return penalty
    

#     def voltage_and_geometry_cost_function(self, voltages_and_params: list[float], adjustable: list[bool], voltages_guess: list[float], 
#                                            fnames: Filenames, geometry_creator):
#         ''' Cost function for simultaneous voltage and geometry optimization '''
#         # Find number of adjustable voltages and geometry params
#         n_adjustable = len((voltages_guess[adjustable]))
        
#         # Get voltages and geometry parameters for the current attempt
#         voltages = voltages_and_params[:n_adjustable] 
#         geometry_params = voltages_and_params[n_adjustable:]

#         # Create geometry for the specific parameters
#         geometry_creator(geometry_params, fnames)

#         # Make .pa# file from .gem file, and then create the rest of he .pa files
#         pa_file = self.gem2pa(fnames.iob_filename.removesuffix('iob') + 'gem') # pa_file = .pa#
#         self.refine(pa_file)

#         # Then change the voltages and perform the fast adjust
#         new_voltages = voltages_guess.copy()
#         new_voltages[adjustable] = voltages
#         self.fastadj(fnames.iob_filename.removesuffix('.iob') + '.pa0', new_voltages)

#         # Then fly ions and load flight data
#         self.fly(fnames.iob_filename, fnames.fly_filename, fnames.rec_filename, fnames.output_filename,
#                  command_type='Flying ions: voltage optimization')
#         df_ic, df_res = self.load_flight_data(fnames.output_filename)

#         # Finally calculate the VMI cost function
#         penalty = 0
#         initial_energies = df_ic['KE'].unique()
#         initial_azimuth = df_ic['Azm'].unique()
#         initial_elevation = df_ic['Elv'].unique()

#         # Calculate VMI penalty as sum of squared detector radius splat difference for each unique velocity vector
#         for energy in initial_energies:
#             for aximuth in initial_azimuth: 
#                 for elevation in initial_elevation:
#                     mask = (df_ic['KE'] == energy) & (df_ic['Azm'] == aximuth) & (df_ic['Elv'] == elevation)
#                     y_pos = df_res.loc[mask]['Y']
#                     if  y_pos.empty:
#                         break
#                     penalty += (y_pos.max() - y_pos.min())**2

#         # Make sure all ions land on the detector
#         for x in df_res['X']:
#             penalty += 3000*(x - 570)**2  

#         # Make sure ions don't go to 'negative' radii
#         for y in df_res['Y']:
#             penalty += 1000 if y < 0 else 0
#             penalty += 1000 if y > 20 else 0

#         # Keep descending voltage order
#         for i in range(len(voltages) - 2): # Minus two due to lens
#             if voltages[i+1] > voltages[i]:
#                 penalty += 500
            
#         print(f'VOLTAGES FOR CURRENT RUN: {voltages}')
#         print(f'GEOMETRY PARAMETERS FOR CURRENT RUN: {geometry_params}')
#         print(f'PENALTY FOR CURRENT RUN: {penalty}')
#         return penalty
    

#     def sequential_geometry_voltage_optimization(self, voltages_and_params: list[float], adjustable: list[bool], voltages_guess: list[float], 
#                                                  fnames: Filenames, geometry_creator) -> float:
#         pass 


