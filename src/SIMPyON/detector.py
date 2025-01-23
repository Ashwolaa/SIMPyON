class Detector:
    def __init__(
        self,
        position=[0, 0, 0],
        energy_scaling: list = [0.0025, 0, 0],
        tof_scaling=0.25,
        label: str = "",
        weight=1,
        charge=1,
        radius=40,
        cost_actions=tuple(),
    ) -> None:
        self.position = position
        self.energy_scaling = energy_scaling
        self.tof_scaling = tof_scaling
        self.label = label
        self.weight = weight
        self.charge = charge
        self.radius = radius
        self.cost_actions = cost_actions

    @property
    def position(self):
        """str: get the title of the module"""
        return self._position

    @position.setter
    def position(self, position: float):
        self._position = position

    @property
    def tof_scaling(self):
        """str: get the title of the module"""
        return self._tof_scaling

    @tof_scaling.setter
    def tof_scaling(self, tof_scaling: float):
        self._tof_scaling = tof_scaling

    @property
    def energy_scaling(self):
        """str: get the title of the module"""
        return self._energy_scaling

    @energy_scaling.setter
    def energy_scaling(self, energy_scaling: list or float):
        self._energy_scaling = energy_scaling

    def update_energy_scaling(self, elim):
        self.energy_scaling[0] = elim / (self.radius) ** 2

    @property
    def label(self):
        """str: get the title of the module"""
        return self._label

    @label.setter
    def label(self, label: bool):
        self._label = label

    @property
    def weight(self):
        """str: get the title of the module"""
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._weight = weight

    @property
    def charge(self):
        """str: get the title of the module"""
        return self._charge

    @charge.setter
    def charge(self, charge):
        self._charge = charge

    @property
    def cost_actions(self):
        """str: get the title of the module"""
        return self._cost_actions

    @cost_actions.setter
    def cost_actions(self, cost_actions):
        self._cost_actions = cost_actions
