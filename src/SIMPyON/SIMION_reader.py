from SIMPyON.filenames import Filenames
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import ListedColormap, CenteredNorm
import pint

ureg = pint.UnitRegistry()
Q_ = pint.Quantity


amu2kg = ureg("amu").to("kg").magnitude
joule2eV = ureg("J").to("eV").magnitude
eV_from_SIMION = 0.5 * 1e6 * amu2kg * joule2eV


class SIMION_reader:
    """SIMION_reader class to read data produced by SIMION."""

    def __init__(
        self, project_dir=None, operating_system="windows", filenames: Filenames = None
    ):
        """"""
        self.project_dir = project_dir
        self.operating_system = operating_system
        self.filenames = filenames
        self.eV_from_SIMION = 0.5 * 1e6 * amu2kg * joule2eV

    @property
    def project_dir(self):
        """str: get the title of the module"""
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir: bool):
        self._project_dir = project_dir

    @property
    def filenames(self):
        """str: get the title of the module"""
        return self._filenames

    @filenames.setter
    def filenames(self, filenames: Filenames):
        self._filenames = filenames

    def plot_geometry(self, ax, fnames: Filenames, electrodes: list):
        """Plot the geometry on a matplotlib axis"""
        # Create pathces from electrode array
        patches_kwargs = {"fc": "black", "ec": "black", "lw": 0.01, "fill": True}
        patches = []
        for electrode in electrodes:
            x_start, x_end = electrode.x_start, electrode.x_end
            r_start, r_end = electrode.r_start, electrode.r_end
            patches.append(
                Rectangle(
                    (x_start, r_start),
                    x_end - x_start,
                    r_end - r_start,
                    **patches_kwargs,
                )
            )
            patches.append(
                Rectangle(
                    (x_start, -r_start),
                    x_end - x_start,
                    -(r_end - r_start),
                    **patches_kwargs,
                )
            )

        # Add pathes to the mpl axis
        for patch in patches:
            ax.add_patch(patch)

        return patches

    def plot_field_lines(
        self,
        ax,
        fnames: Filenames,
        electrodes: list,
        workspace_dimensions=(0, 500, -80, 80),
        cmap="seismic",
        n_lines=65,
    ):
        """Plots field lines and electrode configuration from the PA files and the list of electrodes.

        Arguments
        ---------
        ax : matplotlib axis
            The matplotlib axis on which to plot the setup.
        fnames : Filenames
            The filenames class of the project.
        electrodes : list[CylindricalElectrode]
            A list of the cylindrical electrodes instances of which the setup consists.
        workspace_dimensions : tuple(float, float, float, float)
            A tuple with the dimensions of the workspace in mm.
            Explicitly, it should be in the form (x_min, x_max, y_min, y_max).
        cmap : Any
            A string of colormap instance specifying the colormap to be used for for contours.
        n_lines : int
            The number of field lines to be plotted.

        """
        # pa = PA.PA(file=f'{fnames.iob_filename.removesuffix('.iob')}.pa0')
        pa = PA.PA(file="current_setup.pa0")

        # Find dimensions and make meshgrid
        x, y, z = np.arange(pa.nx()), np.arange(pa.ny()), np.arange(pa.nz())
        X, Y, Z = np.meshgrid(x, y, z)

        # Vectorize and reshape the potential array
        pot = np.vectorize(pa.potential_real)(
            X.flatten(), Y.flatten(), Z.flatten()
        ).reshape(X.shape)
        plt.contour(
            np.concatenate((np.flip(pot[:, :, 0], 0), pot[:, :, 0])),
            n_lines,
            cmap=cmap,
            norm=CenteredNorm(),
            linewidths=0.5,
            extent=workspace_dimensions,
        )
        # Plot all electrodes
        patches = []
        for electrode in electrodes:
            x_start, x_end = electrode.x_start, electrode.x_end
            r_start, r_end = electrode.r_start, electrode.r_end

            patches.append(
                Rectangle(
                    (x_start, r_start),
                    x_end - x_start,
                    (r_end - r_start),
                    facecolor="black",
                    edgecolor="black",
                )
            )

            patches.append(
                Rectangle(
                    (x_start, -r_start),
                    x_end - x_start,
                    -(r_end - r_start),
                    facecolor="black",
                    edgecolor="black",
                    zorder=5,
                )
            )

        coll = PatchCollection(patches, zorder=10, color="k")
        ax.add_collection(coll)
        ax.set_aspect("equal")
        plt.tight_layout()

    def plot_trajectories():
        pass

    @staticmethod
    def loadFlighData(output_file=None, filter=None):
        "Read File and return starting/end conditions"
        if output_file:
            df = pd.read_csv(output_file, skiprows=6, delimiter="\t")
            # Slicing to choose between starting/splash/crossing
            start = df[::2].reset_index()  # Starting conditions
            splash = df[1::2].reset_index()  # Detector splash
            return start, splash

    @staticmethod
    def get_position(df):
        return np.sqrt(
            np.array(df["X"]) ** 2 + np.array(df["Y"]) ** 2 + np.array(df["Z"]) ** 2
        )

    @staticmethod
    def get_radial_position(df):
        return np.sqrt(np.array(df["Y"]) ** 2 + np.array(df["Z"]) ** 2)

    @staticmethod
    def get_Y_velocity(df):
        return np.array(df["Vy"])

    @staticmethod
    def get_Y_position(df):
        return np.array(df["Y"])

    @staticmethod
    def get_Z_position(df):
        return np.array(df["Z"])

    @staticmethod
    def get_X_position(df):
        return np.array(df["X"])

    @staticmethod
    def get_velocity(df):
        return np.sqrt(
            np.array(df["Vx"]) ** 2 + np.array(df["Vy"]) ** 2 + np.array(df["Vz"]) ** 2
        )

    @staticmethod
    def get_radial_velocity(df):
        return np.sqrt(np.array(df["Vy"]) ** 2 + np.array(df["Vz"]) ** 2)

    @staticmethod
    def get_X_velocity(df):
        return np.array(df["Vx"])

    @staticmethod
    def get_ToF(df):
        return np.array(df["TOF"])

    @staticmethod
    def get_mass(df):
        return np.array(df["Mass"])

    @staticmethod
    def get_charge(df):
        return np.array(df["Charge"])

    @staticmethod
    def get_radial_energy(df):
        return (
            SIMION_reader.get_radial_velocity(df) ** 2
            * SIMION_reader.get_mass(df)
            * eV_from_SIMION
        )

    def plot_2D_ion_image(self, output_file, bins=256, cmap="viridis"):
        """Plots a 2D ion image"""
        df_ic, df_fc = self.load_flight_data(output_file.oput_filename)
        img, _, _, _ = plt.hist2d(df_fc["Y"], df_fc["Z"], bins=bins, cmap=cmap)
        plt.gca().set_aspect("equal")
        cbar = plt.colorbar()
        cbar.minorticks_on()
        plt.minorticks_on()
        plt.xlabel("$x$ (mm)")
        plt.ylabel("$y$ (mm)")
        plt.tight_layout()
        return img


def main():
    print("Hello world!")


if __name__ == "__main__":
    main()
