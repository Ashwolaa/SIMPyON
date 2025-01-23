# %%
import toml
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
from SIMPyON.SIMION_reader import SIMION_reader as R
import re
from datetime import datetime, timedelta
from benedict import benedict


def calculate_resolution(output_file, doFit=True):
    start, splash = R.loadFlighData(output_file)
    dic_output = benedict(ion=benedict(), electron=benedict())
    for i_c, charge in enumerate([1, -1]):
        mask = start["Charge"] == charge
        if sum(mask) > 0:
            radE = np.round(R.get_radial_energy(start[mask]), 3)
            r = R.get_radial_position(splash[mask])
            if doFit:
                polyfit = np.polyfit(r, radE, 2, full=True)
                err = []
                errR = []
                r_means = []
                e_unique = np.unique(radE)
                for rE in e_unique:
                    m = rE == radE
                    E = np.polyval(polyfit[0], r[m]) - rE
                    dE = np.max(E) - np.min(E)
                    r_mean = np.mean(r[m])
                    dR = np.max(r[m]) - np.min(r[m])
                    err.append(dE)
                    errR.append(dR / r_mean * 2)
                    r_means.append(r_mean)
                err_e = (np.array(err) / (e_unique + 0.001)) * 100
        if charge == 1:
            output = dic_output.ion
        else:
            output = dic_output.electron
        output.polyfit = polyfit[0]
        output.err = [r_means, err_e]
        output.r_final = r
        output.E_start = radE

    return dic_output


def plotEnergyResolution(dic_outputs,figsize=None):
    colors = ["green", "blue"]
    color_error = ["darkgreen", "darkblue"]
    if figsize is None:
        fig, ax1 = plt.subplots()
    else:
        fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis
    edge = 41
    accuracy = 100
    r_d = np.arange(edge)
    for i_c, (key, output) in enumerate(dic_outputs.items()):
        ax1.plot(output.r_final, output.E_start, "o", label=key, color=colors[i_c])
        # ax1.hist(output.r_final,bins=np.linspace(0,edge,edge*accuracy), color=colors[i_c])
        ax2.plot(output.err[0], output.err[1], "p", color=color_error[i_c])
        ax1.plot(
            r_d,
            np.polyval(output.polyfit, r_d),
            "p",
            markerfacecolor="None",
            markeredgecolor=color_error[i_c],
            markeredgewidth=1
        )
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.set_ylabel("Energie (eV)")
    ax1.set_xlabel("Radius (mm)")
    ax2.set_ylabel("Error \DeltaE / E (%)")
    ax1.legend()

    return fig, ax1, ax2
    #### ADD TOF ####
    # start['']


# def get_std(df):
#     return f'$\sigma_Y$ = {np.std(df['Y'])}\n $\sigma_Z$ = {np.std(df['Z'])}'


# def plotSpatialResolution(output_file):
#     # output_file = self.S.fly_no_input()
#     # ========== read output ==========
#     start, splash = R.loadFlighData(output_file)
#     # ========== loop for each detector ==========
#     fig, axs = plt.subplots(2, 2)
#     for i_c, charge in enumerate([1, -1]):
#         mask = start["Charge"] == charge
#         axs[i_c][0].plot(start[mask]["Y"], start[mask]["Z"], "o")
#         axs[i_c][1].plot(splash[mask]["Y"], splash[mask]["Z"], "o")

#         # get_std(start[mask])
#         axs[i_c][0].set_title(get_std(start[mask]))
#         axs[i_c][1].set_title(get_std(splash[mask]))

#         axs[i_c][0].set_xlabel("Y")
#         axs[i_c][0].set_ylabel("Z")
#         axs[i_c][1].set_xlabel("Y")
#         axs[i_c][1].set_ylabel("Z")
#         # plt.xlabel('Z')
#     fig.tight_layout()
#     # plt.xlim(left=0)
#     # plt.ylim(bottom=0)
#     plt.legend()

#     #### ADD TOF ####
#     # start['']

#     plt.show(block=False)


def makeVoltage(ext_volt, ground_volt, elec_focus, L_electrodes):
    voltage_list = np.zeros((2, L_electrodes))
    for ind, (e_volt, g_volt, e_focus) in enumerate(
        zip(ext_volt, ground_volt, elec_focus)
    ):
        l_ext = L_electrodes - e_focus  # N focusing electrodes
        voltage_list[ind, :e_focus] = (
            (1 + np.arange(e_focus, dtype=float)) * e_volt / e_focus
        )

        focus_volt = (g_volt - voltage_list[ind, e_focus - 1]) / l_ext
        voltage_list[ind, e_focus:] = voltage_list[ind, e_focus - 1] + focus_volt * (
            1 + np.arange(l_ext, dtype=float)
        )

    voltage_list = voltage_list.T.flatten()
    voltage_list = np.append(voltage_list, [0, 0])
    return voltage_list


def makeVoltage3(
    ext_volt, focus_volt, ground_volt, focus_index, ground_index, L_electrodes
):
    voltage_list = np.zeros((2, L_electrodes))
    for ind, (e_volt, f_volt, g_volt, focus_i, ground_i) in enumerate(
        zip(ext_volt, focus_volt, ground_volt, focus_index, ground_index)
    ):
        voltage_list[ind, :focus_i] = (
            (1 + np.arange(focus_i, dtype=float)) * e_volt / focus_i
        )

        L_f = ground_i - focus_i
        focus_step = (f_volt - voltage_list[ind, focus_i - 1]) / L_f

        voltage_list[ind, focus_i:ground_i] = voltage_list[
            ind, focus_i - 1
        ] + focus_step * (1 + np.arange(L_f, dtype=float))

        L_g = L_electrodes - ground_i  # N focusing electrodes
        ground_step = (g_volt - voltage_list[ind, ground_i - 1]) / L_g

        voltage_list[ind, ground_i:] = voltage_list[ind, ground_i - 1] + ground_step * (
            1 + np.arange(L_g, dtype=float)
        )

    voltage_list = voltage_list.T.flatten()
    voltage_list = np.append(voltage_list, [0, 0])
    return voltage_list


def make_voltage_list(factors, voltages_param, L_electrodes):
    if len(factors) > 4:
        return makeVoltage3(
            voltages_param["ext_volt"] * factors[0:2],
            voltages_param["focus_volt"] * factors[2:4],
            voltages_param["ground_volt"] * factors[4:],
            voltages_param["focus_index"],
            voltages_param["ground_index"],
            L_electrodes,
        )
    else:
        return makeVoltage(
            voltages_param["ext_volt"] * factors[0:2],
            voltages_param["ground_volt"] * factors[2:],
            voltages_param["focus_index"],
            L_electrodes,
        )


# %%
%matplotlib Qt
import matplotlib as mpl
import win32gui
import pygetwindow as gw

base_folder = r"C:\Users\constant.schouder\Documents\Python\VMI\Models\ISMO\Test\PEPICO"
# base_folder = r'D:\Work\Python\VMI\Models\PEPICO_ISMO\many-electrodes'
# Regular expression for matching the directory name pattern
pattern = re.compile(r"PEPICO2_\d+-\d+-\d+$")
pattern = re.compile(r"PEPICO_.*?\[8, 12].*$")
# pattern = re.compile(r"PEPICO_unboundElectrons_.*")

pattern = re.compile(r"PEPICO_i\(\d+, \d+, \d+\).*$")
pattern = re.compile(r"PEPICO_i.*?\[8, 16].*$")
pattern = re.compile(r"PEPICO_i\(20, 50,.*?\[8, 16].*$")
pattern = re.compile(r"PEPICO_L15.*?\[8, 16].*$")
pattern = re.compile(r"PEPICO_L30.*?\[8, 8].*$")


lim = -1
doPlot = False
doPlotVoltage = False
L_electrodes = 30
start_index = 1
output_file = "final_output.csv"
# output_file = "temp.csv"


# mpl.rcParams['figure.dpi'] = 100
px = 1/plt.rcParams['figure.dpi']  # pixel in inches
# screen_dpi = mpl.rcParams['figure.dpi']
screen_width, screen_height = gw.getWindowsWithTitle(gw.getActiveWindow().title)[0].size
# Adjust figure size to fit N figures horizontally
figure_width = screen_width / lim * px
figure_height = screen_height / lim * px


# Calculate the cutoff time
cutoff_time = datetime.now() - timedelta(days=2)
# List all directories matching the pattern
matching_dirs = [
    d
    for d in os.listdir(base_folder)
    if os.path.isdir(os.path.join(base_folder, d))
    and pattern.search(d)
    and datetime.fromtimestamp(os.path.getmtime(os.path.join(base_folder, d)))
    > cutoff_time
]

data = benedict()
err = benedict()

for matchin_dir in matching_dirs:
    folder = os.path.join(base_folder, matchin_dir)
    with open(os.path.join(folder, "result.pkl"), "rb") as f:
        data[matchin_dir] = pickle.load(f)
        # print(data[matchin_dir])
    # dic_outputs = calculate_resolution( os.path.join(folder, "final_output.csv"), doFit=True)    
    dic_outputs = calculate_resolution( os.path.join(folder, output_file), doFit=True)    
    err[matchin_dir] = np.mean(dic_outputs.ion.err[1][start_index:])+np.mean(dic_outputs.electron.err[start_index][1:])
lowest_values = sorted(data.items(), key=lambda item: err[item[0]])[:lim]

# lowest_values = sorted(err.items(), key=lambda x: x)[:lim]
# lowest_values = sorted(data.items(), key=lambda x: x[1]["result"].fun)[:lim]
for i, (k, v) in enumerate(lowest_values):
    if doPlot:
        folder = os.path.join(base_folder, k)
        dic_outputs = calculate_resolution( os.path.join(folder, output_file), doFit=True)
        
        fig, ax1, ax2 = plotEnergyResolution(dic_outputs,)
        print(k)
        print(v["result"].x)
        # coeff = np.sum(dic_output["polyfit"])
        ax2.set_ylim([0, 20])

        plt.show(block=False)
        plt.xlim([0, 40])
        plt.ylim([0, 15])
        plt.title(
            f'{k}\n cost = {v['result'].fun}, err = {err[k]}'
        )
        fig.canvas.manager.window.move(
            i * figure_width/px, figure_height/px
        )
    if doPlotVoltage:
        plt.figure()
        plt.plot(make_voltage_list(v["result"].x, v["input"], L_electrodes), "o")
        plt.xlabel("Index")
        plt.ylabel("Voltage")
        plt.title(f'{k}\n cost = {v['result'].fun}')

# %%
from collections import defaultdict

data = dict()
base_folder = r"C:\Users\constant.schouder\Documents\Python\VMI\Models\ISMO\Test\PEPICO"
# base_folder = r'D:\Work\Python\VMI\Models\PEPICO_ISMO\many-electrodes'
# Regular expression for matching the directory name pattern
pattern = re.compile(r"PEPICO_i\(20, 80, 1\).*?\[8, 16].*$")

matching_dirs = [
    d
    for d in os.listdir(base_folder)
    if os.path.isdir(os.path.join(base_folder, d)) and pattern.search(d)
]

# Regex pattern to extract the group key
pattern = re.compile(r"\((\d+, \d+, \d+)\)")

# Dictionary to store grouped strings
grouped = defaultdict(list)

# Group strings by the extracted key
for s in matching_dirs:
    match = pattern.search(s)
    if match:
        key = match.group(1)  # Extract the key (e.g., "20, 70, 1")
        grouped[key].append(s)

costs = benedict()
# Display grouped strings
for key, group in grouped.items():
    # print(f"Group ({key}):")
    tot_cost = 0
    for item in group:
        # print(f"  {item}")
        folder = os.path.join(base_folder, item)
        with open(os.path.join(folder, "result.pkl"), "rb") as f:
            data = pickle.load(f)
            tot_cost += data["result"].fun
    # print(tot_cost)

    costs[key] = tot_cost
a = costs.items_sorted_by_values()
a
