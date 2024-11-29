from SIMPyON.filenames import Filenames
import SIMPyON
import os
import subprocess
import time
class SIMION():

    """SIMION class for running commands in SIMION."""
    def __init__(self, simion_exe_path, project_dir=None, operating_system='windows', filenames: Filenames=None,quiet=True,nogui=True,version='8.1',numthreads=0):
        """"""
        if version ==8.1:
            self.numThreads = True
        else:
            self.numThreads = False

        self.numthreads=numthreads
        self.simion_exe_path = simion_exe_path
        self.quiet = quiet
        self.nogui = nogui
        if os.name=='posix': 
            print('It\'s linux time!')
            self.simion_exe_path = f'/bin/bash -c + {self.simion_exe_path}'        
        if project_dir:
            self.project_dir = project_dir
        else:
            self.project_dir = os.getcwd()      
        self.operating_system = operating_system
        self.filenames = filenames

    @property
    def simion_exe_path(self):
        """str: get the title of the module"""
        return self._simion_exe_path
    @simion_exe_path.setter
    def simion_exe_path(self, simion_exe_path:str):
        self._simion_exe_path = simion_exe_path

    @property
    def project_dir(self):
        """str: get the title of the module"""
        return self._project_dir
    @project_dir.setter
    def project_dir(self, project_dir:str):
        self._project_dir = project_dir

    @property
    def nogui(self):
        """str: get the title of the module"""
        return self._nogui
    @nogui.setter
    def nogui(self, nogui:bool):
        self._nogui = nogui


    @property
    def quiet(self):
        """str: get the title of the module"""
        return self._quiet
    @quiet.setter
    def quiet(self, quiet:bool):
        self._quiet = quiet

    @property
    def filenames(self):
        """str: get the title of the module"""
        return self._filenames
    @filenames.setter
    def filenames(self, filenames:Filenames):
        self._filenames = filenames

    @property
    def numthreads(self):
        """str: get the title of the module"""
        return self._numthreads
    @numthreads.setter
    def numthreads(self, numthreads:int):
        self._numthreads = numthreads

    def simion_command(self, command:str, command_type: str='',quiet=True, nogui=True,numthreads=None):
        """Runs generic SIMION command.
        
        Parameters
        ----------
        command : string
            The command passed to SIMION
        command_type: string
            Type of command
        noprint : boolean
            Used to suppress printing in the terminal. 
            If True, nothing is printed when SIMION commands are run.
            Defaults to False.

        Returns
        -------
        string
            The command string passed to the terminal.
        """
        command_string = ''
        if nogui:
            command_string += '--nogui '
        if self.numThreads and self.numthreads:
                command_string += f'--num-threads={numthreads} '
        command_string += command
        # if noprint:
        #     command = '--quiet '  + command

        exec_string = f'{self.simion_exe_path} {command_string}'

        try:
            start_time = time.time()
            if quiet == False:
                print(f'  {command_type}  '.center(72, '*'))
                print(f'Launching command:')
                print(command_string)
                print('\n')

            if quiet == True:
                check = subprocess.Popen(exec_string, stdout = subprocess.PIPE)
                std_out, std_err = check.communicate()
            else:
                check = subprocess.Popen(exec_string)
            check.wait()
            check.kill()
            if not quiet:
                print(f'Success. Time elapsed: {round(time.time() - start_time, 3)} s')
        except Exception as err:
            print(f'Unexpected error: {err}')

        return exec_string

    # def combine_geometry_file(self,filename,gem_files:list):
    #     if filename.endswith('.gem'):
    #         filename = filename
    #     else:
    #         filename = filename+'.gem'
    #     print(f'Generating geometry file "{filename}"...')        
    #     with open(os.path.join(self.project_dir, f'{filename}'), 'w') as f:
    #         f.write(f'; {header}\n') # header

    def make_geometry_from_electrodes(self,filename,electrodes:list,):
        if filename.endswith('.gem'):
            filename = filename
        else:
            filename = filename+'.gem'        
        with open(os.path.join(self.project_dir, f'{filename}'), 'w') as f:            
            for electrode in electrodes:
                electrode_string = electrode.buildString()                
                f.write(electrode_string)
                f.write('\n')

    def make_gem_to_pa_file(self, filename, input_list:list, dims =(100,100), origin=[0,0,0], scale=1, mirror='', header=''):
        nx,ny=dims
        if filename.endswith('.gem'):
            filename = filename
        else:
            filename = filename+'.gem'    
        pa_define_string = f'pa_define({int(nx)},{int(ny)},{1},cylindrical,{mirror},electrostatic)'

        with open(os.path.join(self.project_dir, f'{filename}'), 'w') as f:
            f.write(f'; {header}\n') # header
            f.write(pa_define_string + '\n\n') # pa_define

            x, y, z = origin
            f.write(f'locate({x},{y},{z},{scale}) ;position in grid units x,y,z,gu/mm\n') # scaling and origin
            f.write(f'{{\n') # scaling and origin
            for input in input_list:
                if issubclass(type(input),SIMPyON.electrodes.Element):
                    electrode_string = input.buildString()                
                    f.write(electrode_string)
                else:
                    f.write(f'include({input})')
                f.write('\n')
            f.write('}')

        print(f'Geometry file "{filename}" generated in working directory:\n{self.project_dir}.')
        print(f'Workbench dimensions: nx = {nx}, ny = {ny}, nz = 1 (gu).')
        return filename

    def make_geometry_file(self, nx, ny, filename, electrodes:list, origin=[0,0,0], scale=1, mirror='', header=''):
        """
        Generates .gem file for an arbitrary number of electrodes. Assumes nz=1, cylindrical PA.

        Arguments
        ---------

        Returns
        -------
        """

        if filename.endswith('.gem'):
            filename = filename
        else:
            filename = filename+'.gem'

        print(f'Generating geometry file "{filename}"...')

        pa_define_string = f'pa_define({int(nx)},{int(ny)},{1},cylindrical,{mirror},electrostatic)'

        with open(os.path.join(self.project_dir, f'{filename}'), 'w') as f:
            f.write(f'; {header}\n') # header
            f.write(pa_define_string + '\n\n') # pa_define

            x, y, z = origin
            f.write(f'locate({x},{y},{z},{scale}) {{\n') # scaling and origin

            for electrode in electrodes:
                electrode_string = electrode.buildString()                
                f.write(electrode_string)
                f.write('\n')

            f.write('}')

        print(f'Geometry file "{filename}" generated in working directory:\n{self.project_dir}.')
        print(f'Workbench dimensions: nx = {nx}, ny = {ny}, nz = 1 (gu).')
        return filename

    def gem2pa(self, gem_file, pa_file=None,numthreads=None):
        """Generates .pa# file from .gem file."""
        if not pa_file:
            pa_file = os.path.splitext(gem_file)[0] + '.pa#'
        command = f'gem2pa {gem_file} {pa_file}'
        self.simion_command(command, command_type='Creating potential array',numthreads=numthreads)
        self.pa_file = pa_file
        return pa_file

    def refine(self, pa_file, pa_indexes:list=[],numthreads=None):
        """Refines potential array"""
        if pa_indexes:
            for pa_index in pa_indexes:
                pa_file =  os.path.splitext(pa_file)[0]+f'.pa{pa_index}'
                self.simion_command(f'refine {pa_file}', command_type='Refining potential array(s)',numthreads=numthreads)
        else:
            self.simion_command(f'refine {pa_file}', command_type='Refining potential array(s)')

    def fastadj(self, pa_file, voltages,numthreads=None):
        """Fast adjust voltage(s) of electrode(s) in .pa0 file."""

        voltage_string = ','.join([f'{index}={voltage}' for index, voltage in enumerate(voltages, start=1)])
        
        self.simion_command(f'fastadj {pa_file} {voltage_string}', command_type='Fast adjusting voltages',numthreads=numthreads)

    def fly(self, iob_file, fly2_file, rec_file, output_file, command_type: str='', 
            no_prompt: bool=False, retain_trajectories: bool=False,numthreads=None):
        """ Fly ions (calculate trajectories) """
        if os.path.exists(f'{output_file}'):
            os.remove(f'{output_file}')

        if retain_trajectories:
            retain_trajectories_val = 1
        else:
            retain_trajectories_val = 0
        
        self.simion_command(f'fly --particles={fly2_file} --restore-potentials=0 --recording={rec_file} --recording-output={output_file} --retain-trajectories={retain_trajectories_val} {iob_file}', 
                            command_type=command_type,numthreads=numthreads)
        return output_file

    def fly_no_input(self,numthreads=None):
        """ Fly ions (calculate trajectories) """
        return self.fly(self.filenames.iob_filename, self.filenames.fly_filename,
                  self.filenames.rec_filename, self.filenames.output_filename,numthreads=numthreads)

    def lua(self,lua_file,command_type: str=''):
        self.simion_command(f'lua {lua_file}', command_type='Running lua file')

    # def make_fly2_file(self, fly_filename: str, masses: list[int], energies: list[float], positions: list[tuple[float, float]], 
    #                    charge: int, n: int=5, theta_start: float=10, theta_step: float=40) -> None:
    #     """ Creates a .fly2-file based on the given parameters """
    #     fly_file = open(fly_filename, 'w')
    #     fly_file.write('particles {\n')
    #     fly_file.write('\tcoordinates = 0,\n')
        
    #     for energy in energies:
    #         fly_file.write('\n')
    #         fly_file.write(f'\t-- KE = {energy} eV\n')
    #         for mass in masses:
    #             for position in positions:
    #                 fly_file.write('\tstandard_beam {\n')
    #                 fly_file.write(f'\t\tke = {energy}, position = vector({position[0]}, {position[1]}, 0), tob = 0,\n')
    #                 fly_file.write(f'\t\tn = {n}, az = 0, el = arithmetic_sequence {{first = {theta_start}, step = {theta_step}}},\n')
    #                 fly_file.write(f'\t\tmass = {mass}, charge = 1,\n')
    #                 fly_file.write('\t},\n')
                    
    #     fly_file.write('}')
    #     fly_file.close()




def main():
    print('Hello world!')

    simion_exe_path = r'C:\Users\constant.schouder\Desktop\Simion\simion-8.0.5.exe'
    project_folder_path = r'C:\Users\constant.schouder\Documents\Python\VMI\Models\Jansen'

    S = SIMION(simion_exe_path,project_folder_path)    
if __name__ == '__main__':
    main()
