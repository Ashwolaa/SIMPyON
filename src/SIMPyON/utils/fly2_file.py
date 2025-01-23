import SIMPyON.utils.strings as s_utils
import os
import numpy as np


def make_fly2_file(fly_filename: str, fly2_group: list) -> None:
    """Creates a .fly2-file based on the given parameters"""
    fly_file = open(fly_filename, "w")
    fly_file.write("particles {\n")
    fly_file.write("\tcoordinates = 0,\n")
    for group in fly2_group:
        if type(group) == dict:
            fly_file.write(make_fly2_group(**group))
        elif type(group) == list:
            [fly_file.write(make_fly2_group(**gr)) for gr in group]
        elif type(group) == str:
            fly_file.write(group)

    fly_file.write("}")
    fly_file.close()
    return fly_filename


def make_fly2_group(group):
    a = 0


def make_fly2_group_cylinder(
    n=100,
    mass=10,
    charge=1,
    kinetic_energy=2,
    position={
        "center": (0, 0, 0),
        "axis": (0, 1, 0),
        "radius": 0.1,
        "length": 3,
        "fill": True,
    },
    direction={"axis": (-1, 0, 0), "half_angle": 180, "fill": True},
    **kwargs,
):
    strings = []
    strings.append("standard_beam {")
    strings.append(f"n = {n},")
    strings.append(f"ke = {kinetic_energy},")
    strings.append(f"mass = {mass},")
    strings.append(f"charge = {charge},")
    strings.append(f"tob = {0},")
    for key in kwargs:
        strings.append(f"{key} = {kwargs[key]},")
    strings.append(make_pos_cylinder(position))
    strings.append(make_dir_cylinder(direction))
    strings.append("},\n")
    strings = s_utils.list_indent(strings, 2)
    return "\n".join(strings)


def make_fly2_group_linesequence(
    n=100,
    mass=10,
    charge=1,
    kinetic_energy=2,
    position={"start": (750, -5, 0), "step": (0, 1, 0), "n": 11},
    direction=(0, 1, 0),
    **kwargs,
):
    strings = []
    strings.append("standard_beam {")
    strings.append(f"n = {n},")
    strings.append(f"ke = {kinetic_energy},")
    strings.append(f"mass = {mass},")
    strings.append(f"charge = {charge},")
    strings.append(f"tob = {0},")
    for key in kwargs:
        strings.append(f"{key} = {kwargs[key]},")
    strings.append(make_pos_linesequence(position))
    strings.append(f"vector{direction}")
    strings.append("},\n")
    strings = s_utils.list_indent(strings, 2)
    return "\n".join(strings)


def fly_particles_cylinder(
    n_part=100,
    ke_list=[
        2,
    ],
    mass=10,
    charge=1,
    center=(0, 0, 0),
    fly_list=[],
):
    for i, ke in enumerate(ke_list):
        fly_dic = {
            "n": n_part,
            "mass": mass,
            "charge": charge,
            "kinetic_energy": ke,
            "position": {
                "center": (center),
                "axis": (0, 0, 1),
                "radius": 0.1,
                "length": 3,
                "fill": True,
            },
            "direction": {"axis": (0, 1, 0), "half_angle": 180, "fill": True},
            "cwf": i,
            "color": 0,
        }
        fly_list.append(fly_dic)
    return fly_list


def fly_particles_linesequence(
    n_part=100,
    ke_list=[
        2,
    ],
    mass=10,
    charge=1,
    center=(0, 0, 0),
    fly_list=[],
):
    for i, ke in enumerate(ke_list):
        fly_dic = {
            "n": n_part,
            "mass": mass,
            "charge": charge,
            "kinetic_energy": ke,
            "position": {
                "center": (center),
                "axis": (0, 0, 1),
                "radius": 0.1,
                "length": 3,
                "fill": True,
            },
            "direction": {"axis": (0, 1, 0), "half_angle": 180, "fill": True},
            "cwf": i,
            "color": 0,
        }
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


def fly_from_dict(
    filename,
    dicts,
    origin,
):
    fly_list = []
    for particle_key, flying_particle in dicts.items():
        if flying_particle["doRun"]:
            n_part = flying_particle["n_part"]
            ke_list = flying_particle["ke_list"]
            mass = flying_particle["mass"]
            charge = flying_particle["charge"]
            origin_temp = (origin + flying_particle["offset"]).tolist()
            if flying_particle["dist"] == "sequence":
                sequence_start = flying_particle["start"]
                sequence_step = flying_particle["start"]

                fly_list = fly_particles_linesequence(flying_particle)
                # fly_list = fly_particles_linesequence(n_part,ke_list,mass=mass,charge=charge,center=tuple(origin_temp),fly_list=fly_list)
    filename = make_fly2_file(filename, fly_list)


def fly_examples(
    filename,
    origin_mm=[0, 0, 0],
    n_part=100,
    ions_list=dict(doRun=True, mass=100, ke_list=np.array([0, 1, 2, 4, 6, 8, 10])),
    electrons_list=dict(doRun=True, ke_list=np.array([0, 1, 2, 4, 6, 8, 10])),
):
    fly_list = []
    if ions_list["doRun"]:
        fly_list = fly_particles(
            n_part,
            ions_list["ke_list"],
            mass=100,
            charge=1,
            center=tuple(origin_mm),
            fly_list=fly_list,
        )
    if electrons_list["doRun"]:
        fly_list = fly_particles(
            n_part,
            electrons_list["ke_list"],
            mass=0.000548579903,
            charge=-1,
            center=tuple(origin_mm),
            fly_list=fly_list,
        )
    filename = make_fly2_file(filename, fly_list)
    return filename


# def make_fly2(filename, launch_dic, )
#     fly_params = launch_dic['fly_params']

#     detector_params = launch_dic['detector_params']

#     for
#     launch_dic['fly_params']

#     ['ions']
#     launch_dic['fly_params']['electrons']
#     ['position_initial']
#     ['position_final']

#     launch_dic['fly_params']['ions']


def vector_str(vector):
    return f"vector({vector[0]}, {vector[1]}, {vector[2]})"


def write_particle(filename, particles_data, fly_type="sequence"):
    """
    Écrit un fichier texte avec les données des particules.

    Arguments :
        filename : str : Le nom du fichier dans lequel écrire les données.
        particles_data : dict : Un dictionnaire contenant les propriétés des particules.
            Exemple :
            {
                "mass": 0.00054857990946,
                "charge": -1,
                "direction": [1, 0, 0],
                "position_initial": [-5, 0, 0],
                "position_final": [5, 0, 0],
                "n": 11,
                "beams": [
                    {"ke": 0.1},
                    {"ke": 0.2}
                ]
            }
    """
    with open(filename, "w") as file:
        file.write("particles {\n")
        file.write("  coordinates = 0,\n")

        for particle_date in particles_data:
            mass = particle_date.get("mass", 0.0)
            charge = particle_date.get("charge", 0)
            direction = particle_date.get("direction", [0, 0, 0])
            position = particle_date.get("position", [0, 0, 0])
            if fly_type == "sequence":
                position_initial = position["initial"]
                position_final = position["final"]
                n = position["n"]
            else:
                n = particle_date.get("n", 1)

            kes = particle_date.get("ke", 0)
            for ke in kes:
                file.write("  standard_beam {\n")
                file.write("    tob = 0,\n")
                if fly_type == "mass":
                    file.write(f'{make_arithmetic_sequence(mass)}\n')
                else:
                    file.write(f"    mass = {mass},\n")
                file.write(f"    charge = {charge},\n")
                file.write(f"    ke = {ke},\n")
                file.write("    cwf = 1,\n")
                file.write("    color = 0,\n")
                file.write(f"    direction = {vector_str(direction)},\n")
                if fly_type == "sequence":
                    file.write(f'{make_pos_line_sequence(position)}\n')
                elif fly_type == "cylinder":
                    file.write(f'{make_pos_cylinder(position)}\n')
                    file.write(f"    n = {n},\n")
                else:
                    file.write(f"    position = {vector_str(position)},\n")
                    file.write(f"    n = {n},\n")
                file.write("  },\n")
        file.write("}\n")


def make_arithmetic_sequence(mass):
    strings_in = f"    mass = arithmetic_sequence \u007b\n"
    strings = []
    strings.append(f'first = {mass['first']},')
    strings.append(f'last = {mass['last']},')
    strings.append(f'n = {mass['n']},')
    strings.append("\u007d,")
    return strings_in + "\n".join(s_utils.list_indent(strings, 3))


def make_pos_line_sequence(position):
    strings_in = f"    position = line_sequence \u007b\n"
    strings = []
    strings.append(f'first = {vector_str(position['first'])},')
    strings.append(f'last = {vector_str(position['last'])},')
    strings.append(f'n = {position['n']},')
    strings.append("\u007d,")
    return strings_in + "\n".join(s_utils.list_indent(strings, 3))


def make_pos_cylinder(position):
    strings_in = f"    position = cylinder_distribution \u007b\n"
    strings = []
    strings.append(f'center = {vector_str(position['center'])},')
    strings.append(f'axis = {vector_str(position['axis'])},')
    strings.append(f'radius = {position['radius']},')
    strings.append(f'length = {position['length']},')
    strings.append(f'fill = {str(position['fill']).lower()},')
    strings.append("\u007d,")
    return strings_in + "\n".join(s_utils.list_indent(strings, 3))


def make_dir_cylinder(direction):
    strings_in = f"direction = cone_direction_distribution \u007b\n"
    strings = []
    # strings.append(f'direction = cone_direction_distribution \u007b')
    strings.append(f'axis = vector{direction['axis']},')
    strings.append(f'half_angle = {direction['half_angle']},')
    strings.append(f'fill = {str(direction['fill']).lower()},')
    strings.append("\u007d,")
    return strings_in + "\n".join(s_utils.list_indent(strings, 3))


def update_fly_file(flying_particles, D, fly_filename, step=10, factor=0.9, fly_type="sequence", **kwargs):
    charges = flying_particles["charges"]
    masses = flying_particles["masses"]
    particles = []
    for (
        charge,
        mass,
    ) in zip(charges, masses):
        
        for d in D:
            if d.charge == charge:
                scaling = d.energy_scaling[0]            
        if fly_type == "sequence":
            position = dict(first=[750, -5, 0], last=[750, 5, 0], n=11)
            n = 11
        elif fly_type == "cylinder":
            position = dict(
                center=[750, 0, 0], axis=[0, 0, 1], radius=0.25, length=10, fill=True
            )
            n = 100
        elif fly_type == "mass":
            if charge == 1:
                mass = dict(first=1, last=300, step=1)
        particle = {
            "direction": [0, 1, 0],
            "position": position,
            "mass": mass,
            "charge": charge,
            "n": n,
            "ke": scaling * factor * np.arange(d.radius + step, step=step) ** 2,
        }
        particles.append(particle)
    write_particle(fly_filename, particles, fly_type)
    return fly_filename

def main():
    # Exemple d'utilisation :
    particles = {
        "mass": 0.00054857990946,
        "charge": -1,
        "direction": [1, 0, 0],
        "position_initial": [-5, 0, 0],
        "position_final": [5, 0, 0],
        "n": 11,
        "ke": np.array([0, 1, 4.5, 9, 16]),
    }



    write_particle_config("particles.txt", particles)

    # print('Hello world!')
    # project_folder_path = r'C:\Users\constant.schouder\Documents\Python\VMI\Models\Test'
    # filename = os.path.join(project_folder_path,'test.fly2')
    # fly_dic_ion = {'n':1000,'mass':10,'charge':1,'kinetic_energy':2,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    # 'color':0,}
    # fly_dic_elect = {'n':1000,'mass':0.000548579903,'charge':-1,'kinetic_energy':2,'position':{'center':(150,0,0),'axis':(0,0,1),'radius':0.1,'length':3,'fill':True},'direction':{'axis':(-1, 0, 0),'half_angle':180,'fill':True},'cwf':1,
    # 'color':0,}
    # # strings = make_fly2_group(**fly_dic)
    # make_fly2_file(filename,[fly_dic_ion,fly_dic_elect])


if __name__ == "__main__":
    main()
