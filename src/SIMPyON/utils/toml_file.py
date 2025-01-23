import os

import toml

import SIMPyON.utils.file_management as f_m
import SIMPyON.utils.fly2_file as fly2_file
from SIMPyON.detector import Detector
from SIMPyON.filenames import Filenames
from SIMPyON.SIMION import SIMION
from SIMPyON.SIMION_PA import SIMION_PA as PA
from SIMPyON.SIMION_reader import SIMION_reader as READER
from SIMPyON.utils.gem_file import get_gem


def prepareLauncher(launcher, fly_type="", quiet=True, nogui=True):
    """_summary_

    Args:
        toml_file (_type_): launcher toml file with dictionnary entries

    Returns:
        _type_: S,R,P,D
    """
    # launcher = toml.load(toml_file)

    workspace = launcher["workspace"]
    paths = launcher["paths"]
    detector_params = launcher["detector_params"]

    # Path
    project_folder_path = paths["project_folder"]
    simion_exe_path = paths["simion_exe"]
    filename = paths["filename"]

    if not os.path.exists(project_folder_path):
        os.mkdir(project_folder_path)
    # Workspace
    origin_mm = workspace["origin_mm"]
    size_x = workspace["size_x"]
    size_y = workspace["size_y"]
    scaling = workspace["scaling"]

    # Making Detectors
    D = makeDetectors(detector_params,)

    F = f_m.makeFiles(project_folder_path, filename)
    # ================================================ Initialize classes ============================================================
    # SIMION class to run simion commands  # noqa: F821
    S = SIMION(
        simion_exe_path,
        project_folder_path,
        filenames=F,
        nogui=True,
        quiet=quiet,
        no_prompt=True,
    )
    R = READER(project_folder_path, filenames=F)
    # SIMION class to read output from SIMION
    P = PA(origin=origin_mm, size=(size_x, size_y), scaling=scaling)
    # SIMION class containing number of points, origin and scaling for the simulations

    # # Making flying file
    F.fly_filename = os.path.join(
        S.project_dir,
        "sliced_imaging.fly2")

    return S, R, P, D, F


# def makeFly(fly_params, fly_filename, origin,detector_params):    
#     import numpy as np
#     # Fly params
#     fly_params['ions']['energy'] = detector_params['ions']['energy_scaling']*(10*np.arange(5))**2
#     fly_params['electrons']['energy'] = detector_params['electrons']['energy_scaling']*(10*np.arange(5))**2
#     fly2_file.fly_from_dict(fly_filename, fly_params, origin)

    # ions_list = fly_params['ions']
    # electrons_list = fly_params['electrons']
    # P.origin

    # fly2_file.fly_examples(fly_filename,origin,n_part=100,ions_list=ions_list,electrons_list=electrons_list)
    # fly2_file.fly_from_dict(fly_filename,fly_params)


def makeDetectors(detector_params,):
    # ================================================ Define detectors ============================================================
    D = []
    for i, (d_key, d_value) in enumerate(detector_params.items()):
        D.append(Detector(**d_value))

    return D

