import os 
import shutil


folder_res = r'C:\Users\constant.schouder\Documents\Python\VMI\Python library\SIMPyON\src\SIMPyON\resources\files'


def checkFile(project_folder_path,filename,ext):
    filename = f'{filename}.{ext}'
    full_path = os.path.join(project_folder_path,filename)
    if not os.path.exists(full_path):
        try:
            shutil.copy2(os.path.join(folder_res,f'setup.{ext}'),full_path)
        except:
            print('No file to copy')

    return filename
