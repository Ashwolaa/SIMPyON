import os
import shutil
from SIMPyON.filenames import Filenames
from pathlib import Path

folder_res = os.path.join(os.getcwd(), r"files")


def checkFile(project_folder_path, filename, ext):
    filename = f"{filename}.{ext}"
    full_path = os.path.join(project_folder_path, filename)
    folder_res = os.path.join(os.path.dirname(__file__), r"resources\files")
    if not os.path.exists(full_path):
        try:
            shutil.copy2(os.path.join(folder_res, f"base.{ext}"), full_path)
        except:
            print("No file to copy")

    return filename


def makeFiles(project_folder_path, filename):
    # ================================================ Initialize files ============================================================
    iob_file = checkFile(
        project_folder_path, filename, "iob"
    )  # Make sure that iob and rec files exist
    rec_file = checkFile(project_folder_path, filename, "rec")
    fly_file = os.path.join(project_folder_path, f"{filename}.fly2")
    output_file = os.path.join(project_folder_path, f"temp.csv")
    gem_file = os.path.join(project_folder_path, f"{filename}.gem")

    F = Filenames(
        project_folder_path=project_folder_path,
        iob_filename=iob_file,
        rec_filename=rec_file,
        fly_filename=fly_file,
        output_filename=output_file,
        gem_file=gem_file,
    )

    return F


def saveOutput(project_output_path, file_lists):
    if not os.path.isdir(project_output_path):
        os.mkdir(
            project_output_path,
        )
    for file in file_lists:
        P = Path(file)
        file_out = os.path.join(project_output_path, P.name)
        shutil.copy2(file, file_out)
