
import numpy as np
import os
import re

def makeElement(string):
    A = string.replace('\t','').split('\n') #Remove indent and split newlines
    origin = A[0]
    array = extract_numbers(origin)
    locate = np.array(array[:2])
    scale = array[3]
    index = array[4]    
    element,parameters = extract_word_and_numbers(A[8])
    if element =='box2D':
        width = np.array([parameters[0],parameters[2]])
        radius = np.array([parameters[1],parameters[3]])
        return CylindricalElement(index,width,radius,locate,scale)
    elif element =='polyline':
        edges = tuple(parameters)
        return PolyLineElement(index,edges,locate,scale)
    else:
        return None
    
def makeElements(string_list):
    return [makeElement(string) for string in string_list]


def extract_numbers(strings):
    # Utilisation de l'expression régulière pour trouver tous les nombres
    numbers = re.findall(r'-?\d+', strings)
    # Conversion des nombres trouvés en entiers
    numbers = [int(number) for number in numbers]
    return numbers

def extract_word_and_numbers(strings):
    # Utilisation de l'expression régulière pour extraire le mot et les nombres
    result = re.match(r'(\w+)\((.*)\)', strings)    
    if result:
        keyword = result.group(1)
        numbers = extract_numbers(result.group(2))
        return keyword, numbers
    else:
        return None, None

class Element():
    def __init__(self, index=None, locate=np.array([0,0,0]), scale=1, element='e', adjustable=True,label=''):
        self.index = index
        self.label = label
        self.element = element
        self.locate = locate
        self.scale = scale
        self.adjustable = adjustable
    
    @property
    def index(self,):
        return self._index   
    @index.setter
    def index(self,index):
        self._index = index    
    @property
    def locate(self,):
        return self._locate  
    @locate.setter
    def locate(self,locate):
        if type(locate)==int or type(locate)==np.float64:
            locate = np.concatenate([[locate],[0,0]])
        elif type(locate) is np.ndarray:
            if len(locate)==1:
                locate = np.concatenate([locate,[0,0]])
            elif len(locate)==2:
                locate = np.concatenate([locate,[0]])
        self._locate= locate    
    @property
    def scale(self,):
        return self._scale   
    @scale.setter
    def scale(self,scale):
        self._scale = scale    
    @property
    def element(self,):
        return self._element        
    @element.setter
    def element(self,element):
        self._element = element   
    @property
    def label(self,):
        return self._label        
    @label.setter
    def label(self,label):
        self._label = label   
        
    def makeIndex(self,):
        return f'{self.index}'
    
    def makeLocate(self,):
            return f'locate{self.locate[0],self.locate[1],self.locate[2],self.scale}'+self.makeLabel()
        
    def makeElement(self,):
        if self.element:
            return f'{self.element}({self.index})'   
        else:
            return ''                     
    
    # def makeLabel(self,label='Electrode'):
    #     return f'; {label}\n'

    def makeElementString(self,):
        #### TO BE SUBCLASSED #####
        pass
    
    # def buildString(self,):
    #     """Generates string """
    #     self.tab_index = 0            
    #     strings = ''
    #     strings += self.makeLabel()
    #     strings += self.makeLocate()        
    #     strings += '\n\t{\n'
    #     strings +='\t'+self.makeElement()
    #     strings += '\n\t\t{\n'
    #     strings += '\t\tfill'
    #     strings += '\n\t\t\t{\n'
    #     strings += '\t\t\twithin'
    #     strings += '\n\t\t\t\t{\n'
    #     strings += f'\t\t\t\t{self.makeElementString()}\n'
    #     strings += '\t\t\t\t}\n'
    #     strings += '\t\t\t}\n'
    #     strings += '\t\t}\n'
    #     strings += '\t}\n'        
    #     return strings
    
    def buildString(self,):
        self.tab_index = 0 
        strings = []
        strings_in = [self.makeLocate(),self.makeElement(),'fill','within']  
        for s in strings_in:
            strings.append(self.makeIndent(s))
            strings.append(self.makeBrackets(s,1))
        strings.append(self.makeIndent(self.makeElementString()))
        self.tab_index += 1
        for s in strings_in:
            strings.append(self.makeBrackets(s,-1))
        return '\n'.join(strings)

    def makeIndent(self,cmd):
        return '\t'*int(self.tab_index)+cmd   
    
    def makeBrackets(self, cmd ='', direction=0):
        self.tab_index += direction
        if direction>0:
            cmd = '{'            
        elif direction<0:
            cmd = '}'        
        return self.makeIndent(cmd)     
    

    def get_electrode_string(self,):
        return self.buildString()
    
    def makeLabel(self,label='Element'):
            return f'; {label} {self.index}'
    


class CylindricalElement(Element):
    def __init__(self, index, width = np.array([0,1]), radius = np.array([0,10]), locate=np.array([0,0,0]), scale=1, element=None, adjustable=True,label=''):        
        Element.__init__(self, index, locate, scale, element, adjustable,label)
        self.width = width
        self.radius = radius

    @property
    def width(self,):
        return self._width    
    @width.setter
    def width(self,width):
        if type(width)==int:
            width = np.concatenate([[0],[width]])
        elif type(width) is np.ndarray:
            if len(width)==1:
                width = np.concatenate([[0],[width]])
        self._width = width
    @property
    def radius(self,):
        return self._radius   
    @radius.setter
    def radius(self,radius):
        self._radius = radius


    def makeElementString(self,):
        box = f'box2D({self.width[0]},{self.radius[0]},{self.width[1]},{self.radius[1]})'
        return box

    # def findParameters(self,strings,)
        
    def makeLabel(self,label='Cylindrical'):
            return f'; {label} {self.index}'
    
    
class PolyLineElement(Element):
    def __init__(self, index, edges,  locate=np.array([0,0,0]), scale=1, element=None, adjustable=True,label=''):        
        Element.__init__(self, index, locate, scale, element, adjustable,label)
        self.edges = edges

    def makeElementString(self,):
        #Return array for polygone electrodes, each set of (x,y) represent a corner
        if len(self.edges)>4:
            box=f'polyline{self.edges}'
            return box        
        else:
            print('Not enough data points')       

    def makeLabel(self,label='PolyLine'):
        return f'; {label} {self.index}'


def main():
    print('Hello world!')
    #Workben in mm
    origin=np.array([352,0,0]) # in mm
    size_x,size_y = np.array([1000,200]) # in mm
    scaling = 1 # in gu/mm
    #Going to grid units
    nx = size_x*scaling # in gu
    ny = size_y*scaling # in gu
    origin*=scaling # in gu

    b = CylindricalElement(0,width=(0,2),radius=(7.5,15),locate=(7.5,0,0)).buildString()
    c = CylindricalElement(1,width=(0,2),radius=(7.5,15),locate=(15,0,0)).buildString()

    # ### JANSEN VMI ####
    # e = [electrode(0,[7.5,0,0],1).makeElectrode(0,[0,2],[7.5,15]),
    #      electrode(1,[27.5,0,0],1).makeElectrode(0,[0,2],[10,20]),
    #      electrode(2,[57.5,0,0],1).makeElectrode(0,[0,2],[15,30]),
    #      electrode(3,[-9.5,0,0],1).makeElectrode(0,[0,2],[10,20]),
    #      electrode(4,[-29.5,0,0],1).makeElectrode(0,[0,2],[15,30]),
    #      electrode(5,[-59.5,0,0],1).makeElectrode(0,[0,2],[20,40]),]


if __name__ == '__main__':
    main()

