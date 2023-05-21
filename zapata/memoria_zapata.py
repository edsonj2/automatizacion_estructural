from pylatex import Document, Section, Subsection,Subsubsection
from pylatex import Tabular, Table, MultiColumn
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from tkinter.filedialog import askopenfilename
import shutil

def copy_image(url):
    archivo_seleccionado = askopenfilename()
    shutil.copy(archivo_seleccionado, 'out/' + url)

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

from memoria import ecuaciones, introduccion
doc.append(NoEscape(ecuaciones))
doc.append(NoEscape(introduccion))
from memoria import presiones, req_min
doc.append(NoEscape(presiones))
doc.append(NoEscape(req_min))

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

#Dimensiones de la columna:
b_col = 60*cm
h_col = 90*cm

def set_variables(var_dict):
    text = ''
    for name,data in var_dict.items():
        value = data[0]
        unit = data[1]
        text+=f"\\FPset\\{name}{{{value.to(unit).magnitude:.2f}}}\n"
    return text

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

# sec.append(subsec)
# doc.append(sec)
# doc.append(NoEscape(var))
# doc.append(NoEscape(c_portante))
# doc.append(factor_suelo(1,'S0'))
# doc.generate_pdf('out/mem_zapata')
# doc.generate_tex('out/mem_zapata')

from memoria import cap_portante_2
c_portante = cap_portante_2(σt,γc,hz,γm,hs,hp,SCpiso,σsn)


sec.append(subsec)
doc.append(sec)
#doc.append(NoEscape(var))
doc.append(NoEscape(c_portante))
# doc.append(factor_suelo(1,'S0'))

doc.generate_pdf('out/mem_zapata')
doc.generate_tex('out/mem_zapata')
