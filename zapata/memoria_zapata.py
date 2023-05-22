from pylatex import Document, Section, Subsection,Subsubsection
from pylatex import Tabular, Table, MultiColumn
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from tkinter.filedialog import askopenfilename
import shutil

from memoria import ecuaciones, datos

geometry_options = { "left": "2.5cm", "top": "1.5cm" }
doc = Document(geometry_options=geometry_options)
doc.packages.append(Package('xcolor', options=['dvipsnames']))
doc.packages.append(Package('graphicx'))
doc.packages.append(Package('xargs'))
doc.packages.append(Package('subfigure'))
doc.packages.append(Package('array'))
doc.packages.append(Package('multicol'))
doc.packages.append(Package('multirow'))
doc.packages.append(Package('fp'))
doc.packages.append(Package('xcolor'))
doc.packages.append(Package('booktabs'))
doc.packages.append(Package('amsmath'))

doc.append(NoEscape(ecuaciones))

def copy_image(url):
    archivo_seleccionado = askopenfilename()
    shutil.copy(archivo_seleccionado, 'out/' + url)

def set_variables(var_dict):
    text = ''
    for name,data in var_dict.items():
        value = data[0]
        unit = data[1]
        text+=f"\\FPset\\{name}{{{value.to(unit).magnitude:.2f}}}\n"
    return text

def tex_py(texto):
    return texto.replace('{', '{{').replace('}', '}}').replace('[','[{').replace(']','}]')

#Uso de variables
import pint
ureg = pint.UnitRegistry()
m = ureg('m')
cm = ureg('cm')
kgf = ureg('kgf')
ureg.define('tonf=1000*kgf')
tonf = ureg('tonf')

sec = Section('Diseño de la Cimentación')
subsec = Subsection('Diseño de Zapata Aislada')
subsubsec = Subsubsection('Datos para el diseño de una zapata aislada con carga y momentos')

subsec.append(NoEscape(datos))

#Datos de la columna:
b_col=0.3*m
h_col=0.7*m

#Capacidad Portante del terreno
σt = 1.2*kgf/cm**2
hz = 10*cm
γc = 2400*kgf/m**3
γm = 1400*kgf/m**3
hs = 100*cm
hp = 40*cm
SCpiso = 100*kgf/m**2
σsn = σt - γc*hz - γm*hs - γc*hp - SCpiso
σsn

variables = {
    'sigmat':(σt,'kgf/cm**2'),
    'gammac':(γc,'kgf/m**3'),
    'hz':(hz,'m'),
    'gammam':(γm,'kgf/m**3'),
    'hs':(hs,'m'),
    'hp':(hp,'m'),
    'SC':(SCpiso,'kgf/m**2'),
    'sigmas':(σsn,'kgf/cm**2')
}
var = set_variables(variables)
var1 = set_variables(h_col)
var2 = set_variables(b_col)

from memoria import cap_portante_2
c_portante = cap_portante_2(σt,γc,hz,γm,hs,hp,SCpiso,σsn)

texto = r'''
\begin{align*}
	L &= \LongitudZapL[7.77][0.80][0.40] = 3.10\\
	B &= \LongitudZapB[7.77][0.80][0.40] = 2.70\\
	A &= \Area[3.10][2.70] = 
\end{align*}
'''


sec.append(subsec)
doc.append(sec)
doc.append(NoEscape(c_portante))

doc.generate_pdf('out/mem_zapata')
doc.generate_tex('out/mem_zapata')
