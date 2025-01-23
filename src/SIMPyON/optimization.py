import scipy.optimize as opt
import numpy as np
from SIMPyON.detector import Detector
from SIMPyON.SIMION_reader import SIMION_reader
from SIMPyON.SIMION import SIMION
import matplotlib.pyplot as plt
from scipy.optimize import Bounds
import pickle
import os


# ================================== Cost Functions ==================================


def cost_energy_scaling(energy, splash, energy_scaling):
    """
    Calculate the cost based on the energy scaling model.
    Args:
        energy: Array of initial energies.
        splash: Array of splash data.
        energy_scaling: Polynomial coefficients for energy scaling.
    Returns:
        The sum of squared differences between actual and predicted energy.
    """
    return np.sum((energy - np.polyval(energy_scaling, splash)) ** 2)


def cost_detector_hit(hitPos, det_pos):
    """
    Calculate the cost of deviation from the detector's target position.
    Args:
        hitPos: Array of hit positions.
        det_pos: Target position of the detector.
    Returns:
        The sum of squared differences between hit positions and the detector position.
    """
    return np.sum((hitPos - det_pos[0]) ** 2)


def cost_func(cost, cost_scale):
    """
    Scale the computed cost by a scaling factor.
    Args:
        cost: The raw cost value.
        cost_scale: Scaling factor to weight the cost.
    Returns:
        Scaled cost.
    """
    return cost * cost_scale


def cost_spatial_spread(Vys, Ys):
    """
    Calculate the cost based on spatial spread.
    Args:
        Vys: Array of Y-velocity values.
        Ys: Array of Y-positions.
    Returns:
        The sum of squared deviations of Y-positions grouped by Y-velocity.
    """
    cost = 0
    for Vy in np.unique(Vys):
        mask = Vy == Vys
        cost += np.sum((Ys[mask] - np.mean(Ys[mask])) ** 2)
    return cost


def cost_time_spread(ToF, X_start):
    """
    Calculate the cost based on time-of-flight spread.
    Args:
        ToF: Array of time-of-flight values.
        X_start: Array of initial X-positions.
    Returns:
        The sum of squared deviations of ToF grouped by X_start.
    """
    cost = 0
    for x in np.unique(X_start):
        mask = x == X_start
        cost += np.sum((ToF[mask] - np.mean(ToF[mask])) ** 2)
    return cost


# ================================== Optimization Class ==================================


class Optimization:
    """
    A class to optimize voltage settings for ion trajectory simulations.
    """

    def __init__(
        self,
        simion_instance: SIMION,
        simion_reader: SIMION_reader,
        detectors: list,
        make_voltage_func=None,
    ) -> None:
        """
        Initialize the optimization class with simulation, reader, and detector instances.
        """
        self.S = simion_instance
        self.R = simion_reader
        self.D = detectors
        self.make_voltage_list = make_voltage_func

    # ================================================ Optimizer ============================================================
    def optimize_voltages(self, factors, voltages_params):
        """
        Optimize the voltages using given factors and parameters.
        Args:
            factors: Scaling factors for voltage adjustment.
            voltages_params: Parameters for the voltage adjustment function.
        Returns:
            Total cost of the simulation for the given voltages.
        """        
        voltage_list = self.make_voltage_list(factors, voltages_params)
        # ========== adjust voltages ==========
        self.S.fastadj(pa_file=self.S.filenames.pa_file, voltages_list=voltage_list)
        # ========== flying ions ==========
        check = self.S.fly_no_input()
        if check.returncode == 0:  # Check for successful run
            cost = 0
            start, splash = self.R.loadFlighData(self.S.filenames.output_filename)
            # Calculate cost for each detector
            for i_c, charge in enumerate([1, -1]):
                mask = start["Charge"] == charge
                if np.sum(mask) > 0:
                    cost += self.calculate_cost(start[mask], splash[mask], self.D[i_c])
            # ========== return cost ==========
        else:
            cost = 1e10 # Penalize unsuccessful runs
        return cost

    # ================================================ Cost functions ============================================================
    def calculate_cost(self, start, splash, detector: Detector):
        """
        Calculate the total cost based on various criteria for a single detector.
        """        
        cost = 0
        if "detector_hit" in detector.cost_actions:
            # ========== Detector hit ==========
            cost += cost_func(
                cost_detector_hit(splash["X"], detector.position),
                cost_scale=1000 * detector.weight,
            )
        if "time_spread" in detector.cost_actions:
            # ========== Detector hit ==========
            cost += cost_func(
                cost_time_spread(splash["ToF"], start["X"]),
                cost_scale=1 * detector.weight,
            )
        if "energy_scaling" in detector.cost_actions:
            # ========== Energy scaling ==========
            cost += 1 * cost_func(
                cost_energy_scaling(
                    self.R.get_radial_energy(start),
                    self.R.get_radial_position(splash),
                    detector.energy_scaling,
                ),
                cost_scale=1 * detector.weight,
            )
        if "spatial_spread" in detector.cost_actions:
            # ========== Spatial spread ==========
            cost += cost_func(
                cost_spatial_spread(
                    self.R.get_Y_velocity(start), self.R.get_Y_position(splash)
                ),
                cost_scale=1 * detector.weight,
            )
        return cost

    # ================================================ Minimize function ============================================================
    def minimize(self, voltages_param, starting_factors=None, doSave=True):
        """
        Minimize the total cost function using the Nelder-Mead optimization method.
        """        
        if starting_factors is None:
            starting_factors = np.ones(4)

        # ================================================ Setup bounds ============================================================
        lb, ub = (
            np.zeros_like(starting_factors),
            np.ones_like(starting_factors) * np.inf,
        )
        bounds = Bounds(lb, ub)
        # ================================================ Setup optimizer ============================================================
        args = (voltages_param,)
        minimizer_kwargs = {
            "method": "Nelder-Mead",
            "options": {
                "disp": True,
                "fatol": 300,
                "maxfev": 500,
                "maxiter": 300,
                "adaptive": True,
                "xatol": 1e-2,
            },
            "args": args,
            "bounds": bounds,
        }
        self.result = opt.minimize(
            self.optimize_voltages, starting_factors, **minimizer_kwargs
        )
        if doSave:
            self.store_result(voltages_param)
        return self.result

    # ================================================ Do plot ============================================================
    def plotResolution(self):
        """
        Plot the resolution and the radial energy vs position for each detector.
        """        
        output_file = self.S.fly_no_input()
        # ========== read output ==========
        start, splash = self.R.loadFlighData(output_file)
        # ========== loop for each detector ==========
        plt.figure()
        for i_c, charge in enumerate([1, -1]):
            mask = start["Charge"] == charge
            if sum(mask) > 0:
                radE = self.R.getRadialEnergy(start[mask])
                r = self.R.getRadialPosition(splash[mask])
                cost = self.calculate_cost(start[mask], splash[mask], self.D[i_c])
                polyfit = np.polyfit(r, radE, 2, full=True)
                plt.plot(r, radE, "o", label=charge)
                plt.plot(r, np.polyval(polyfit[0], r), "o", label=f"Cost:{cost}")
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.legend()
        plt.show(block=False)

    def store_result(self, input_parameters):
        """
        Save the optimization results to a file.
        """        
        self.ouput = os.path.join(self.S.project_dir, "result.pkl")
        with open(self.ouput, "wb") as f:
            stored = dict(result=self.result, input=input_parameters)
            pickle.dump(stored, f)
