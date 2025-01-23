from SIMPyON.filenames import Filenames
import SIMPyON
import os
import subprocess
import time


class SIMION:
    """SIMION class for running commands in SIMION."""

    def __init__(
        self,
        simion_exe_path,
        project_dir=None,
        operating_system="windows",
        filenames: Filenames = None,
        quiet=True,
        nogui=True,
        version="8.1",
        numthreads=0,
        no_prompt=True,
    ):
        """"""
        if version == 8.1:
            self.numThreads = True
        else:
            self.numThreads = False
        self.no_prompt = no_prompt
        self.numthreads = numthreads
        self.simion_exe_path = simion_exe_path
        self.quiet = quiet
        self.nogui = nogui
        if os.name == "posix":
            print("It's linux time!")
            self.simion_exe_path = f"/bin/bash -c + {self.simion_exe_path}"
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
    def simion_exe_path(self, simion_exe_path: str):
        self._simion_exe_path = simion_exe_path

    @property
    def project_dir(self):
        """str: get the title of the module"""
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir: str):
        self._project_dir = project_dir

    @property
    def nogui(self):
        """str: get the title of the module"""
        return self._nogui

    @nogui.setter
    def nogui(self, nogui: bool):
        self._nogui = nogui

    @property
    def quiet(self):
        """str: get the title of the module"""
        return self._quiet

    @quiet.setter
    def quiet(self, quiet: bool):
        self._quiet = quiet

    @property
    def filenames(self):
        """str: get the title of the module"""
        return self._filenames

    @filenames.setter
    def filenames(self, filenames: Filenames):
        self._filenames = filenames

    @property
    def numthreads(self):
        """str: get the title of the module"""
        return self._numthreads

    @numthreads.setter
    def numthreads(self, numthreads: int):
        self._numthreads = numthreads

    def simion_command(
        self,
        command: str,
        command_type: str = "",
        quiet=True,
        nogui=True,
        numthreads=None,
        timeout=10,
    ):
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
        command_string = ""
        if nogui:
            command_string += "--nogui "
        if self.no_prompt:
            command_string += "--noprompt "
        if self.numThreads and self.numthreads:
            command_string += f"--num-threads={numthreads} "
        command_string += command

        exec_string = f"{self.simion_exe_path} {command_string}"

        try:
            start_time = time.time()
            if quiet == False:
                print(f"  {command_type}  ".center(72, "*"))
                print(f"Launching command:")
                print(command_string)
                print("\n")

            if self.quiet == True:
                check = subprocess.Popen(exec_string, stdout=subprocess.PIPE)
                std_out, std_err = check.communicate(timeout=timeout)
            else:
                check = subprocess.Popen(exec_string)
            check.wait(timeout=timeout)
            check.kill()
            if not self.quiet:
                print(f"Success. Time elapsed: {round(time.time() - start_time, 3)} s")
        except Exception as err:
            print(f"Unexpected error: {err}")

        return check

    def gem2pa(self, gem_file, pa_file=None, numthreads=None):
        """Generates .pa# file from .gem file."""
        if not pa_file:
            pa_file = os.path.splitext(gem_file)[0] + ".pa#"
        command = f"gem2pa {gem_file} {pa_file}"
        self.simion_command(
            command, command_type="Creating potential array", numthreads=numthreads
        )
        self.pa_file = pa_file
        return pa_file

    def refine(self, pa_file, pa_indexes: list = [], numthreads=None, timeout=60):
        """Refines potential array"""
        if pa_indexes:
            for pa_index in pa_indexes:
                pa_file = os.path.splitext(pa_file)[0] + f".pa{pa_index}"
                return self.simion_command(
                    f"refine {pa_file}",
                    command_type="Refining potential array(s)",
                    numthreads=numthreads,
                    timeout=timeout,
                )
        else:
            return self.simion_command(
                f"refine {pa_file}",
                command_type="Refining potential array(s)",
                timeout=timeout,
            )

    def fastadj(self, pa_file, voltages_list, index_list=None, numthreads=None):
        """Fast adjust voltage(s) of electrode(s) in .pa0 file."""
        if index_list is None:
            voltage_string = ",".join(
                [
                    f"{index}={voltage}"
                    for index, voltage in enumerate(voltages_list, start=1)
                ]
            )
        else:
            voltage_string = ",".join(
                [
                    f"{index}={voltage}"
                    for index, voltage in zip(voltages_list, index_list)
                ]
            )

        return self.simion_command(
            f"fastadj {pa_file} {voltage_string}",
            command_type="Fast adjusting voltages",
            numthreads=numthreads,
        )

    def fly(
        self,
        iob_file=None,
        fly2_file=None,
        rec_file=None,
        output_file=None,
        command_type: str = "",
        retain_trajectories: bool = False,
        numthreads=None,
        timeout=30,
    ):
        """Fly ions (calculate trajectories)"""
        if os.path.exists(f"{output_file}"):
            os.remove(f"{output_file}")
        if iob_file is None:
            iob_file = self.filenames.iob_filename
        if fly2_file is None:
            fly2_file = self.filenames.fly_filename
        if rec_file is None:
            rec_file = self.filenames.rec_filename
        if retain_trajectories:
            retain_trajectories_val = 1
        else:
            retain_trajectories_val = 0

        return self.simion_command(
            f"fly --particles={fly2_file} --restore-potentials=0 --recording={rec_file} --recording-output={output_file} --retain-trajectories={retain_trajectories_val} {iob_file}",
            command_type=command_type,
            numthreads=numthreads,
            timeout=timeout,
        )

    def fly_no_input(self, numthreads=None):
        """Fly ions (calculate trajectories)"""
        return self.fly(
            self.filenames.iob_filename,
            self.filenames.fly_filename,
            self.filenames.rec_filename,
            self.filenames.output_filename,
            numthreads=numthreads,
        )

    def lua(self, lua_file, *args):
        cmd = f"lua {lua_file}"
        for arg in args:
            cmd += f" {arg}"
        print(cmd)
        return self.simion_command(f"{cmd}", command_type="Running lua file")


def main():
    print("Hello world!")

    simion_exe_path = r"C:\Users\constant.schouder\Desktop\Simion\simion-8.0.5.exe"
    project_folder_path = (
        r"C:\Users\constant.schouder\Documents\Python\VMI\Models\Jansen"
    )

    S = SIMION(simion_exe_path, project_folder_path)


if __name__ == "__main__":
    main()
