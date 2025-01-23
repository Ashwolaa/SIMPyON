import os

class Filenames:
    """ Class for keeping track of filenames and directories """

    def __init__(self, project_folder_path: str, rec_filename: str, fly_filename: str, output_filename: str, iob_filename: str, gem_file: str):
        """Initializes the necessary directories and filenames for running SIMION simultions
        
        Parameters
        ----------
        project_folder_path: str
            Path to the project folder. Either relative or absolute.     
        rec_filename: str
            The filename of the recording file, for saving data from flights. Include file extension.
        fly_filename: str
            The filename of the fly-file. Include file extension.
        output_filename: str
            The filename of the file for outputting flight data determined by the .rec file. Includes file extension.
        iob_filename: str
            The workspace filename. Includes file extension.
        """

        if os.path.isdir(project_folder_path):
            self.project_folder_path = project_folder_path
        else:
            pass 
        if rec_filename:
            self.rec_filename = os.path.join(project_folder_path,rec_filename)
        if fly_filename:
            self.fly_filename = os.path.join(project_folder_path,fly_filename)
        if output_filename:
            self.output_filename = os.path.join(project_folder_path,output_filename)
        if gem_file:
            self.gem_file = os.path.join(project_folder_path,gem_file)
        if iob_filename:
            self.iob_filename  = os.path.join(project_folder_path,iob_filename)       
            self.pa_file = os.path.join(project_folder_path,os.path.splitext(iob_filename)[0] + '.pa#')          

    def __str__(self):
        return str([f'project_folder_path = {self.project_folder_path}', 
                f'rec_filename = {self.rec_filename}',
                f'fly_filename = {self.fly_filename}',
                f'output_filename = {self.output_filename}',
                f'iob_filename = {self.iob_filename}'])




    def get_filenames(self,):
        return [self.rec_filename,self.fly_filename,self.output_filename,self.iob_filename,self.pa_file,self.gem_file]