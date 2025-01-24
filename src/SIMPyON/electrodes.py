import numpy as np
import re
from SIMPyON.utils.strings import numpy_string


def makeElement(string):
    A = string.replace("\t", "").split("\n")  # Remove indent and split newlines
    origin = A[0]
    array = extract_numbers(origin)
    locate = np.array(array[:2])
    scale = array[3]
    index = array[4]
    element, parameters = extract_word_and_numbers(A[8])
    if element == "box2D":
        width = np.array([parameters[0], parameters[2]])
        radius = np.array([parameters[1], parameters[3]])
        return CylindricalElement(index, width, radius, locate, scale)
    elif element == "polyline":
        edges = tuple(parameters)
        return PolyLineElement(index, edges, locate, scale)
    else:
        return None


def makeElements(string_list):
    return [makeElement(string) for string in string_list]


def extract_numbers(strings):
    # Utilisation de l'expression régulière pour trouver tous les nombres
    numbers = re.findall(r"-?\d+", strings)
    # Conversion des nombres trouvés en entiers
    numbers = [int(number) for number in numbers]
    return numbers


def extract_word_and_numbers(strings):
    # Utilisation de l'expression régulière pour extraire le mot et les nombres
    result = re.match(r"(\w+)\((.*)\)", strings)
    if result:
        keyword = result.group(1)
        numbers = extract_numbers(result.group(2))
        return keyword, numbers
    else:
        return None, None



# Base class for geometric elements
class Element:
    """Class used to create string for gem files"""

    def __init__(
        self,
        index=None,
        locate=np.array([0, 0, 0]),
        scale=1,
        element="e",
        adjustable=True,
        label="",
    ):
        self.index = index
        self.label = label
        self.element = element
        self.locate = locate
        self.scale = scale
        self.adjustable = adjustable

    # Property methods for encapsulation of attributes
    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def locate(self):
        return self._locate

    @locate.setter
    def locate(self, locate):
        if type(locate) is int or isinstance(locate, np.generic):
            locate = np.concatenate([[locate], [0, 0]])
        elif type(locate) is np.ndarray:
            if len(locate) == 1:
                locate = np.concatenate([locate, [0, 0]])
            elif len(locate) == 2:
                locate = np.concatenate([locate, [0]])
        self._locate = locate

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    @property
    def element(self):
        return self._element

    @element.setter
    def element(self, element):
        self._element = element

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    # Helper methods to generate descriptive strings
    def makeIndex(self):
        return f"{self.index}"

    def makeLocate(self):
        locate = numpy_string(
            self.locate,
        )
        locate = ",".join(locate)
        return f"locate({locate},{self.scale})" + self.make_label()

    def makeElement(self):
        if self.element:
            return f"{self.element}({self.index})"
        else:
            return ""

    def make_element_string(self):
        # To be overridden by subclasses
        pass

    def buildString(self):
        # Generate a string representation of the element
        self.tab_index = 0
        strings = []
        strings_in = [
            self.makeLocate(),
            self.makeElement(),
            "fill",
        ]
        for s in strings_in:
            strings.append(self.make_indent(s))
            strings.append(self.make_brackets(1, 1))
        strings.append(self.make_element_string())
        # self.tab_index += 1
        for s in strings_in:
            strings.append(self.make_brackets(-1, -1))
        return "\n".join(strings)

    def make_indent(self, cmd):
        return "\t" * int(self.tab_index) + cmd

    def make_brackets(self, direction=0, tab_change=0):
        self.tab_index += tab_change
        if direction > 0:
            cmd = "{"
        elif direction < 0:
            cmd = "}"
        return self.make_indent(cmd)

    def get_electrode_string(
        self,
    ):
        return self.buildString()

    def make_label(self, label="Element"):
        return f"; {label} {self.index}"


# CylindricalElement subclass
class CylindricalElement(Element):
    def __init__(
        self,
        index,
        width=np.array([0, 1]),
        radius=np.array([0, 10]),
        locate=np.array([0, 0, 0]),
        scale=1,
        element="e",
        adjustable=True,
        label="",
    ):
        Element.__init__(self, index, locate, scale, element, adjustable, label)
        self.width = width
        self.radius = radius

    # Property methods for width and radius
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        if type(width) is int or isinstance(width, np.generic):
            width = np.concatenate([[0], [width]])
        elif type(width) is np.ndarray:
            if len(width) == 1:
                width = np.concatenate([[0], [width]])
        self._width = width

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius):
        self._radius = radius

    def make_element_string(self):
        # Build the string representation of the element
        width = numpy_string(self.width)
        box = f"box2D({width[0]},{self.radius[0]},{self.width[1]},{self.radius[1]})"
        string_in = []
        string_in.append(self.make_indent("within"))
        string_in.append(self.make_brackets(1, 1))
        string_in.append(self.make_indent(box))
        string_in.append(self.make_brackets(-1, 0))
        return "\n".join(string_in)

    def make_label(self, label="Cylindrical"):
        return f"; {label} {self.index}"


# PolyLineElement subclass
class PolyLineElement(Element):
    def __init__(
        self,
        index,
        edges,
        locate=np.array([0, 0, 0]),
        scale=1,
        element="e",
        adjustable=True,
        label="",
    ):
        Element.__init__(self, index, locate, scale, element, adjustable, label)
        self.edges = edges

    def make_element_string(self):
        # Return array for polygone electrodes, each set of (x,y) represent a corner
        edges = numpy_string(self.edges)
        edges = ",".join(edges)
        if len(self.edges) > 4:
            box = f"polyline({edges})"
            string_in = []
            string_in.append(self.make_indent("within"))
            string_in.append(self.make_brackets(1, 1))
            string_in.append(self.make_indent(box))
            string_in.append(self.make_brackets(-1, 0))
            return "\n".join(string_in)
        else:
            print("Not enough data points")

    def make_label(self, label="PolyLine"):
        return f"; {label} {self.index}"


# ParabolaElement subclass
class ParabolaElement(Element):
    def __init__(
        self,
        index,
        edges,
        vertex,
        width=1,
        isHalf=True,
        locate=np.array([0, 0, 0]),
        scale=1,
        element="e",
        adjustable=True,
        label="",
    ):
        Element.__init__(self, index, locate, scale, element, adjustable, label)

        self.width = width  # used for # x0+width,y0,x1,y1+width
        self.edges = edges  # x0,y0,x1,y1
        self.vertex = vertex
        self.isHalf = isHalf

    def make_element_string(self):
        # Draw two parabola and substract outter one to inner one to achieve constant width on edges

        v0x, v0y, f0 = self.calculate_focus(
            self.vertex[0], self.vertex[1], self.edges[0], self.edges[1]
        )
        v1x, v1y, f1 = self.calculate_focus(
            self.vertex[0],
            self.vertex[1] + abs(self.width),
            self.edges[0] + self.width,
            self.edges[1],
        )

        string_in = []

        string_in.append(self.make_indent("within_inside"))
        string_in.append(self.make_brackets(1, 1))
        string_in.append(self.make_indent(self.writeParabola(v0x, v0y, f0)))

        if self.isHalf:
            box = f"box2D({v0x},{v0y},{self.edges[0]},{self.edges[1]})"
        else:
            box = f"box2D({-self.edges[0]},{v0y},{self.edges[0]},{self.edges[1]})"

        string_in.append(self.make_indent(box))
        string_in.append(self.make_brackets(-1, 0))
        # string_in.append(self.make_indent("notin"))
        # string_in.append(self.make_brackets(1, 0))
        # string_in.append(self.make_indent(self.writeParabola(v1x, v1y, f1)))
        # string_in.append(self.make_brackets(-1, 0))

        return "\n".join(string_in)

    def calculate_focus(self, vertex_x, vertex_y, edge_x, edge_y):
        return (
            vertex_x,
            vertex_y,
            abs(1 / 4 * (edge_x - vertex_x) ** 2 / (edge_y - vertex_y)),
        )

    def writeParabola(self, x, y, f):
        box = f"parabola({x},{y},{f})"
        return box

    def make_label(self, label="PolyLine"):
        return f"; {label} {self.index}"


############################ Convenient functions to make electrodes #################################


def makeElectrode(
    ind,
    width=(0, 1),
    radius=(0, 100),
    locate=np.array([0, 0, 0]),
    add_scaling=1,
    label="",
):
    return CylindricalElement(
        ind,
        width=width,
        radius=radius,
        locate=locate,
        scale=add_scaling,
        element="e",
        label=label,
    )


def makePolyLine(
    ind, width=1, radius=(0, 100), angle=0, locate=np.array([0, 0, 0]), add_scaling=1
):
    angle = np.deg2rad(angle)
    x_end = np.round((radius[1] - radius[0]) * np.tan(angle))
    # Going from top as origin of electrode
    # [(0,r1);(-w,r1);(-w-x,r0);(-x,r0)] or [(0,r1);(w,r1);(w+x,r0);(x,r0)]
    edges = (0, radius[1], width, radius[1], x_end + width, radius[0], x_end, radius[0])
    return PolyLineElement(
        ind, edges=edges, locate=locate, scale=add_scaling, element="e"
    )


def makeParabola(
    ind,
    width=1,
    edges=(0, 100),
    vertex=(20, 10),
    isHalf=True,
    locate=np.array([0, 0, 0]),
    add_scaling=1,
):
    return ParabolaElement(
        ind,
        width=width,
        edges=edges,
        vertex=vertex,
        isHalf=isHalf,
        locate=locate,
        scale=add_scaling,
        element="e",
    )


def main():
    print("Hello world!")
    # Workben in mm


if __name__ == "__main__":
    main()
