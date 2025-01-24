import SIMPyON.utils.strings as s_utils
from SIMPyON.electrodes import (
    Element,
    makeElement,
    makePolyLine,
    makeElectrode,
    makeParabola,
)
import os
import numpy as np
from pathlib import Path
import toml


def assert_gem_file(filename):
    P = Path(filename)
    if P.suffix != ".gem":
        filename = filename + ".gem"
    return P


def make_geometry_from_electrodes(
    filename,
    electrodes: list[Element],
):
    P = assert_gem_file(filename)
    with open(f"{P}", "w") as f:
        for electrode in electrodes:
            if issubclass(type(electrode), Element):
                electrode_string = electrode.buildString()
                f.write(electrode_string)
                f.write("\n")
    return filename


def make_gem_to_pa_file(
    filename,
    input_list: list[Element, str],
    dims=(100, 100),
    origin=[0, 0, 0],
    scale=1,
    mirror="",
    header="",
):
    nx, ny = dims
    P = assert_gem_file(filename)

    pa_define_string = (
        f"pa_define({int(nx)},{int(ny)},{1},cylindrical,{mirror},electrostatic)"
    )

    with open(P, "w") as f:
        f.write(f"; {header}\n")  # header
        f.write(pa_define_string + "\n\n")  # pa_define

        x, y, z = origin
        f.write(
            f"locate({x},{y},{z},{scale}) ;position in grid units x,y,z,gu/mm\n"
        )  # scaling and origin
        f.write("{{\n")  # scaling and origin
        for input in input_list:
            if issubclass(type(input), Element):
                electrode_string = input.buildString()
                f.write(electrode_string)
            else:
                f.write(f"include({input})")
            f.write("\n")
        f.write("}")

    print(f'Geometry file "{filename}" generated in working directory:\n{P.parent}.')
    print(f"Workbench dimensions: nx = {nx}, ny = {ny}, nz = 1 (gu).")
    return filename


def toml_to_gem(gem_toml, folder_path, file_out=None):
    gem_files = []
    # index = 0
    for det_type_key in gem_toml:  # Loop through electrodes role
        det_types = gem_toml[det_type_key]
        det_gem = f"{det_type_key}.gem"
        elec_ = []
        for det_key in det_types:  # Loop through electrodes with same role
            # index += 1
            selected_det = det_types[det_key]
            if selected_det["type"] == "Polyline":
                index = selected_det["index"]
                offset = selected_det["offset"]
                radius = selected_det["radius"]
                angle = selected_det["angle"]
                width = selected_det["width"]
                elec_.append(
                    makePolyLine(
                        index, width=width, radius=radius, angle=angle, locate=offset
                    )
                )
            elif selected_det["type"] == "Electrode":
                index = selected_det["index"]
                offset = selected_det["offset"]
                radius = selected_det["radius"]
                width = selected_det["width"]
                elec_.append(
                    makeElectrode(index, width=width, radius=radius, locate=offset)
                )
            elif selected_det["type"] == "Parabola":
                index = selected_det["index"]
                offset = selected_det["offset"]
                edges = selected_det["edges"]
                vertex = selected_det["vertex"]
                isHalf = selected_det["isHalf"]
                width = selected_det["width"]
                elec_.append(
                    makeParabola(
                        index,
                        width=width,
                        edges=edges,
                        vertex=vertex,
                        isHalf=isHalf,
                        locate=offset,
                    )
                )
        gem_file = make_geometry_from_electrodes(
            os.path.join(folder_path, det_gem), elec_
        )
        gem_files.append(gem_file)

    return gem_files


def get_gem(filename=None):
    with open(filename, "r") as f:
        strings = f.read()
        strings = strings.split("locate")[1:]
        strings = ["locate" + string for string in strings]
        elec = [makeElement(string) for string in strings]
    return elec


def main():
    print("Hello world!")

if __name__ == "__main__":
    main()
