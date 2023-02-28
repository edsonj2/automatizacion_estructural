import sys
import os
sys.path.append(os.getcwd())


import latex_utils as ltx
from pylatex import Document, Section, Subsection,Subsubsection, Tabular, NoEscape, MiniPage, Center, MultiColumn, Table, Figure, Tabularx
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from pylatex.base_classes import Environment
from ordered_set import OrderedSet
import pandas as pd
import warnings
warnings.simplefilter('ignore', category=Warning)



def mybox3(title):
    mbox = Environment()
    mbox._latex_name = 'tcolorbox'
    mbox.options = NoEscape(r'colback=gray!5!white,colframe=Maroon!75!black,fonttitle=\bfseries,title=%s'%title)
    return mbox

def mybox2(title):
    mbox = Environment()
    mbox._latex_name = 'tcolorbox'
    mbox.options = NoEscape(r'colback=gray!5!white,colframe=cyan!75!black,fonttitle=\bfseries,title=%s'%title)
    return mbox


def factor_zona(obj,zona,insert='',o_type=Subsubsection):
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    
    
    df = [['4','0.45'],['3','0.35'],['2','0.25'],['1','0.10']]
    df[4-zona][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+df[4-zona][1]+r'}}'
    df[4-zona] = [i+r'\cellcolor[rgb]{ .949,  .949,  .949} ' for i in df[4-zona]]
    df = [['Zona','Z'],]
    
    
    with obj.create(o_type('Factor de Zona')):
        obj.append(insert)
        with obj.create(Table(position='ht!')) as tab:
            with obj.create(MiniPage(width='0.55\\textwidth')) as mp:
                    mp.append(NoEscape(r'\caption{Factor de zona}'))
                    with obj.create(Tabular(r'|>{\centering\arraybackslash}m{3.75cm}|>{\centering\arraybackslash}m{3.75cm}|')) as table:
                        table.add_hline()
                        table.add_row((MultiColumn(2, align='|c|', data=bold('FACTOR DE ZONA SEGÚN E-030')),))
                        table.add_hline()
                        table.add_row((NoEscape('\\textbf{ZONA}'), NoEscape('\\textbf{Z}')))
                        table.add_hline()
                        for row in df:
                                table.add_row((NoEscape(row[0]), NoEscape(row[1])))
                                table.add_hline()
                    
            with obj.create(MiniPage(width='0.35\\textwidth')):
                with obj.create(Center()):
                    obj.append(NoEscape('\\includegraphics[width=4cm]{mapa_zona}'))
            tab.append(NoEscape(r'\caption*{Fuente: E-30 (2018)}'))
        

def factor_suelo(obj,zona,suelo,insert='',o_type=Subsubsection):
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('slashbox'))
    
    suelo_ind = {'S0':1,'S1':2,'S2':3,'S3':4}
    data = [['4','0.80','1.00','1.05','1.10'],
            ['3','0.80','1.00','1.15','1.20'],
            ['2','0.80','1.00','1.20','1.40'],
            ['1','0.80','1.00','1.60','2.00']]
    data[4-zona][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[4-zona][suelo_ind[suelo]] +r'}}'
    data[4-zona] = [i+r'\cellcolor[rgb]{ .949,  .949,  .949} ' for i in data[4-zona]]
    data = [[j+r'\cellcolor[rgb]{ .949,  .949,  .949} ' if i ==suelo_ind[suelo] else j for i,j in enumerate(row)]  for row in data]
    
    
    
    with obj.create(o_type('Factor de suelo')):
        obj.append(insert)
        with obj.create(Table(position='ht!')) as tab:
            tab.append(NoEscape(r'\centering'))
            tab.append(NoEscape(r'\caption{Factor de zona}'))
            with obj.create(Tabular(r'|>{\centering\arraybackslash}m{3.75cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as table:
                table.add_hline()
                table.add_row((MultiColumn(5, align='|c|', data=bold('FACTOR DE SUELO SEGÚN E-030')),))
                table.add_hline()
                table.add_row(NoEscape(r'\backslashbox{\textit{\textbf{ZONA}}}{\textit{\textbf{SUELO}}}'),bold('S0'),bold('S1'),bold('S2'),bold('S3'))
                table.add_hline()
                for row in data:
                    table.add_row([NoEscape(i) for i in row])
                    table.add_hline()
            tab.append(NoEscape(r'\caption*{Fuente: E-30 (2018)}'))
    

def periodos_suelo(obj,suelo,insert='',o_type=Subsubsection):
    suelo_ind = {'S0':1,'S1':2,'S2':3,'S3':4}
    
    data = [['Tp','0.30','0.40','0.60','1.00'],
            ['Tl','3.00','2.50','2.00','1.60']]
    data[0][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[0][suelo_ind[suelo]]+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949} '
    data[1][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[1][suelo_ind[suelo]]+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949} '
    
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    
    with obj.create(o_type('Periodos de suelo')):
        obj.append(insert)
        
        with obj.create(Table(position='ht!')) as tab:
            tab.append(NoEscape(r'\centering'))
            tab.append(NoEscape(r'\caption{Periodos de suelo}'))
            with obj.create(Tabular(r'|>{\centering\arraybackslash} m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as table:
                table.append(NoEscape(r'\cline{2-5}'))
                table.add_row((MultiColumn(1,align='r|',data=''),MultiColumn(4,align='c|',data=NoEscape('\\textbf{PERIODO "Tp" y "Tl" SEGÚN E-030}'))))
                table.append(NoEscape(r'\cline{2-5}'))
                table.add_row((MultiColumn(1,align='r|',data=''),MultiColumn(4,align='c|',data=NoEscape(r'\textit{\textbf{Perfil de suelo}}'))))
                table.append(NoEscape(r'\cline{2-5}'))  
                table.add_row((MultiColumn(1,align='r|',data=''),bold('S0'),bold('S1'),bold('S2'),bold('S3')))
                table.add_hline()
                for row in data:
                    table.add_row([NoEscape(i) for i in row])
                    table.add_hline()
            tab.append(NoEscape(r'\caption*{Fuente: E-30 (2018)}'))


def sist_estructural(obj,insert='',o_type=Subsubsection):
    
    data = [['Acero:',''],
            ['Porticos Especiales Resistentes a Momento (SMF)',8],
            ['Porticos Intermedios Resistentes a Momento (IMF)',5],
            ['Porticos Ordinarios Resistentes a Momento (OMF)',4],
            ['Porticos Ordinarios Resistentes a Momento (OMF)',7],
            ['Porticos Ordinarios Concentricamente Arrriostrados (OCBF)',4],
            ['Porticos Excentricamente Arriostrados (EBF)',8],
            ['Concreto Armado:',''],
            ['Porticos',8],
            ['Dual',7],
            ['De muros estructurales',6],
            ['Muros de ductilidad limitada',4],
            [r'\textbf{Albañilería Armada o Confinada}',3],
            [r'\textbf{Madera}',7]]
    
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    
    with obj.create(o_type('Sistema Estructural')):
        obj.append('Después de realizar el análisis sísmico se determino que los sistemas estructurales en X, Y son:')
        obj.append(insert)
        
        with obj.create(Table(position='ht!')) as tab:
            tab.append(NoEscape(r'\caption{coeficiente básico de reducción}'))
            with obj.create(Tabular(r'|>{\arraybackslash}m{10cm}| >{\centering\arraybackslash}m{4cm}|')) as table:
                table.add_hline()
                table.add_row((MultiColumn(2,align='|c|',data=bold('SISTEMAS ESTRUCTURALES')),))
                table.add_hline()
                table.add_row((bold('Sistema Estructural'),MultiColumn(1,align=NoEscape('m{4cm}|'),data=bold('Coeficiente Básico de Reducción Ro'))))
                table.add_hline()
                for row in data:
                    if row[1]:
                        table.add_row([NoEscape(i) for i in row])
                        table.add_hline()
                    else:
                        table.add_row((MultiColumn(2,align='|l|',data=bold(row[0])),))
                        table.add_hline()
            tab.append(NoEscape(r'\caption*{Fuente: E-30 (2018)}'))
            
            

def factor_amplificacion(obj,insert='',o_type=Subsubsection):
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('amsmath'))
    doc.packages.append(Package('caption'))
    
    eq = r'''
    \begin{align*}
        &T< T_{P}         &   C&=2,5\cdot\left ( \frac{T_{P}}{T} \right )\\
        &T_{P}< T< T_{L}  &   C&=2,5\cdot\left ( \frac{T_{P}}{T} \right )\\
        &T> T_{L}         &   C&=2,5\cdot\left ( \frac{T_{P}\;T_{L}}{T^{2}} \right )
    \end{align*}'''
            
    with obj.create(o_type('Factor de Amplificación sísmica')):
        obj.append(insert)
        obj.append('Se determina según el artículo 11 de la E-30')
        obj.append(NoEscape(r'\setlength{\jot}{0.5cm}'))
        with obj.create(Figure(position='h!')):
            obj.append(NoEscape(r'\caption{Factor de amplificación}'))
            with obj.create(MiniPage(width=r'0.5\textwidth')):
                obj.append(NoEscape(eq))
            with obj.create(MiniPage(width=r'0.4\textwidth')):
                obj.append(NoEscape(r'\centering'))
                obj.append(NoEscape('\\includegraphics[width=6.5cm]{Amplificacion}'))
            obj.append(NoEscape(r'\caption*{Fuente: Muñoz (2020)}'))


def factor_importancia(obj,categoria,insert='',o_type=Subsubsection):
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('xcolor'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('multirow'))

    
    cat_ind = {'A1':0,'A2':1,'B':2,'C':3,'D':4}
    data = [['A Edificaciones Escenciales','A1: Establecimiento del sector salud (públicos y privados) del segundo y tercer nivel, según lo normado por el ministerio de salud.','Con aislamiento 1.0 y sin aislamiento 1.5.'],
            ['','A2: Edificaciones escenciales para el manejo de las emergencias, el funcionamiento del gobierno y en general aquellas que puedan servir de refugio después de un desastre.','1.50'],
            ['B Edificaciones Importantes ','Edificaciones donde se reúnen gran cantidad de personas tales como cines, teatros, estadios, coliseos, centros comerciales, terminales de buses de pasajeros, establecimientos penitenciarios, o que guardan patrimonios valiosos como museos y bibliotecas.',r'1.30'],
            ['C Edificaciones Comunes','Edificaciones comunes tales como: viviendas, oficinas, hoteles, restaurantes, depósitos e instalaciones industriales cuya falla no acarree peligros adicionales de incendios o fugas de contaminantes.',r'1.00'],
            ['D Edificaciones temporales','Construcciones provisionales para depósitos, casetas y otras similares.','A criterio del proyectista']]
    
    data[0][0] = r'\multirow{2}[4]{3cm}{'+data[0][0] + '}'
    data[cat_ind[categoria]][2] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{' + data[cat_ind[categoria]][2] + r'}}'
    if cat_ind[categoria] < 2:
        data[cat_ind[categoria]] = [data[cat_ind[categoria]][0]] + [i + r'\cellcolor[rgb]{1,  .949,  .8}' for i in data[cat_ind[categoria]][1:]]
    else:
        data[cat_ind[categoria]] = [i + r'\cellcolor[rgb]{ .949,  .949,  .949}' for i in data[cat_ind[categoria]]]
    data = [row[:2]+[r'\multicolumn{1}{>{\centering\arraybackslash}m{2.8cm}|}{'+row[2]+'}'] for row in data]
        
    with obj.create(o_type('Factor de Importancia')):
        obj.append(insert)
        with obj.create(Table(position='h!')):
            obj.append(NoEscape('\centering'))
            obj.append(NoEscape('\caption{Factor de Uso o Importancia}'))
            with obj.create(Tabular(NoEscape(r'|>{\arraybackslash}m{3cm}|m{8cm}|>{\arraybackslash}m{2.8cm}|'))) as table:
                table.add_hline()
                table.add_row((MultiColumn(3,align='|c|',data=bold('CATEGORIA DE LA EDIFICACION')),))
                table.add_hline()
                table.add_row((MultiColumn(1,align='|c|',data=bold('CATEGORIA')),MultiColumn(1,align='|c|',data=bold('DESCRIPCION')),MultiColumn(1,align='|c|',data=bold('FACTOR U'))))
                table.add_hline()
                table.add_row([NoEscape(i) for i in data[0]])
                table.append(NoEscape(r'\cline{2-3}'))
                for row in data[1:]:
                    table.add_row([NoEscape(i) for i in row])
                    table.add_hline()
            obj.append(NoEscape(r'\caption*{Fuente: E-30 (2018)}'))



def ana_modal(obj,table,insert='',o_type=Subsection):
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('array'))
        
    with obj.create(o_type(r'Análisis modal Art. 26.1 E-030')):
        mbox = mybox3(r'Art. 26.1.1')
        mbox.append(NoEscape(r'\textit{En cada dirección se consideran aquellos modos de vibración cuya suma de masas efectivas sea por lo menos el 90\% de la masa total, pero se toma en cuenta por lo menos los tres primeros modos predominantes en la dirección de análisis.}'))
        obj.append(mbox)
        mbox2 = mybox3(r'Art. 26.1.2')
        mbox2.append(NoEscape(r'\textit{En cada dirección se consideran aquellos modos de vibración cuya suma de masas efectivas sea por lo menos el 90\% de la masa total, pero se toma en cuenta por lo menos los tres primeros modos predominantes en la dirección de análisis.}'))
        obj.append(mbox2)
        
        obj.append(insert)
        
        table = table.astype(float).style.hide(axis='index')
        table.format('{:.3f}')
        table.format('{:.0f}',subset= pd.IndexSlice[:,'Mode'])
        table = table.to_latex(hrules=True,column_format = 'c'*8,)
        
        with obj.create(Table(position='h!')):
            obj.append(NoEscape(r'\extrarowheight = -0.3ex'))
            obj.append(NoEscape(r'\renewcommand{\arraystretch}{1.3}'))
            obj.append(NoEscape('\centering'))
            obj.append(NoEscape('\caption{Periodos y porcentajes de masa participativa}'))
            obj.append(NoEscape(table))



def irreg_rigidez(obj,sis_x,sis_y,insert='',o_type=Subsubsection):
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    
    def latex_table(table):
        table = table[['Story','OutputCase','VX','VY','lat_rig(k)','0.7_prev_k','0.8k_prom','is_reg']]
        table.columns = ['Story','OutputCase','VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)','is\_reg']
        for i in ['VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.3f}',subset=pd.IndexSlice[:,['VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)']])
        table = table.to_latex(hrules=True, column_format = 'c'*8).replace('0.000','')
        return table
    
    
    with obj.create(o_type('Irregularidad de Rigidez-Piso Blando')):
        
        mbox = mybox2('Tabla N°9 E-030')
        mbox.append(NoEscape('Existe irregularidad de rigidez cuando, en cualquiera de las direcciondes de análisis, en un entrepiso la rigidez lateral es menor que 70\% de la rigidez lateral del entrepiso inmediato superior, o es menor que 80\\% de la rigidez lateral promedio de los tres niveles superiores adyacentes. \n Las rigideces laterales pueden calcularse como la razón entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relatibo en el centro de masas, ambos evaluados para la misma condición de carga '))
        obj.append(mbox)
        mbox2 = mybox2('Tabla N°9 E-030')
        mbox2.append(NoEscape('''
Existe irregularidad extrema de rigidez cuando, en cualquiera de las direcciones de análisis, en un entrepiso la rigidez lateral es menor que 60\\% de la rigidez lateral del entrepiso inmediato superior, o es menor que 70\\% de la rigidez lateral promedio de los tres niveles superiores adyacentes.
Las rigideces laterales pueden calcularse como la razon entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relativo en el centro de masas, ambos evaluados para la misma condición de carga.'''))
        obj.append(mbox2)
        
        obj.append(insert)
        
        sis_x = latex_table(sis_x)
        sis_y = latex_table(sis_y)
        
        
        with obj.create(Table(position='h!')):
            obj.append(NoEscape('\centering'))
            obj.append(NoEscape('\caption{Irregularidad de rigidez}'))
            obj.append(NoEscape(sis_x))
            
        with obj.create(Table(position='h!')):
            obj.append(NoEscape('\centering'))
            obj.append(NoEscape('\caption{Irregularidad de rigidez}'))
            obj.append(NoEscape(sis_y))
        

def irreg_masa(obj,masa,insert='',o_type=Subsubsection):
    def latex_table(table):
        table.columns = ['Story','Masa','1.5 Masa Piso Inferior','1.5 Masa Piso Superior','Tipo de Piso','is\_reg']
        table = table.replace('',0.0)
        for i in  ['Masa','1.5 Masa Piso Inferior','1.5 Masa Piso Superior']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.3f}',subset=pd.IndexSlice[:,['Masa','1.5 Masa Piso Inferior','1.5 Masa Piso Superior']])
        table = table.to_latex(hrules=True, column_format = 'c'*6).replace('0.000','')
        return table
    
    
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    
    with obj.create(o_type('Irregularidad de Masa o Peso')):
        mbox = mybox2('Tabla N°9 E-030')
        mbox.append(NoEscape('Se tiene irregularidad de masa (o peso) cuando el peso de un piso determinado según el artículo 26, es nayor que 1,5 veces el peso de un piso adyascente. Este criterio no se aplica en azoteas ni en sótanos'))
        obj.append(mbox)
        obj.append(insert)
        
        with obj.create(Table(position='h!')):
            obj.append(NoEscape('\centering'))
            obj.append(NoEscape('\caption{Irregularidad de Masa o Peso}'))
            obj.append(NoEscape(latex_table(masa)))
    

def irreg_torsion(obj,sis_x,sis_y,insert='',o_type=Subsubsection):
    def latex_table(table):
        table.columns = ['Story', 'OutputCase', 'Direction', 'Max Drift', 'Avg Drift', 'Ratio', 'Height', 'Drifts', '< Driftmax/2', 'Es Regular']
        table = table.style.hide(axis='index')
        # table = table.format('{:.3f}',subset=pd.IndexSlice[:,['Masa','1.5 Masa Piso Inferior','1.5 Masa Piso Superior']])
        table = table.to_latex(hrules=True, column_format = 'c'*10)
        return table
    
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('graphicx'))
    
    with obj.create(o_type('Irregularidad Torsional')):
        mbox = mybox2('Tabla N°9 E-030')
        mbox.append(NoEscape('Existe irregularidad torsional cuando, en cualquiera de las direcciones de análisis el desplazamiento relativo de entrepiso en un edificion ($\\Delta_{max}$) en esa dirección, calculado incluyendo excentricidad accidental, es mayor que 1,3 veces el desplazamineto relativo promedio de los extremos del mismo entrepiso para la condicion de carga ($\Delta_{prom}$). \n Este crriterio sólo se aplica en edificios con diafragmas rígidos y sólo si el máximo desplazamiento relativo de entrepiso es mayor que 50\\% del desplazamiento permisible indicado en la Tabla N° 11'))
        obj.append(mbox)
        mbox2 = mybox2('Tabla N°9 E-030')
        mbox2.append(NoEscape('Existe irregularidad torsional cuando, en cualquiera de las direcciones de análisis el desplazamiento relativo de entrepiso en un edificion ($\\Delta_{max}$) en esa dirección, calculado incluyendo excentricidad accidental, es mayor que 1,5 veces el desplazamineto relativo promedio de los extremos del mismo entrepiso para la condicion de carga ($\Delta_{prom}$). \n Este crriterio sólo se aplica en edificios con diafragmas rígidos y sólo si el máximo desplazamiento relativo de entrepiso es mayor que 50\\% del desplazamiento permisible indicado en la Tabla N° 11'))
        obj.append(mbox)
        obj.append(insert)
        
        table = Table(position='ht!')
        table.append(NoEscape('\centering'))
        table.append(NoEscape('\caption{Irregularidad Torsional}'))
        table.append(NoEscape('\\resizebox{\\textwidth}{!}{'))
        table.append(NoEscape(latex_table(sis_x)+'}'))
        obj.append(table)
        
        table2 = Table(position='ht!')
        table2.append(NoEscape('\centering'))
        table2.append(NoEscape('\caption{Irregularidad Torsional}'))
        table2.append(NoEscape('\\resizebox{\\textwidth}{!}{'))
        table2.append(NoEscape(latex_table(sis_y)+'}'))
        obj.append(table2)
    

def irreg_esquinas(obj,sec_change=None,openings=None,insert='',o_type=Subsubsection):
    '''
    recibe el objeto y produce un informe de irregularidad de esquinas entrante
    sintaxis de sec_change (diccionario):
        {aligerdo: (longitud,espesor),
         macisa: (longitud,esperor)}
        tipo de seccion 1: [longitud,espesor]
    sintaxis de openings:
        aberturas : [(largo, ancho),]
        area_planta: area 
    '''
    
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('array'))
    doc.packages.append(Package('float'))
    
    with obj.create(o_type('Irregularidad por Esquinas Entrantes')):
        mbox = mybox2('Tabla N°9 E-030')
        mbox.append(NoEscape(r'\textit{La estructura se califica como irregular cuando los diafragmas tienen discontinuidades abruptas o variaciones importantes en rigidez, incluyendo aberturas mayores que 50\% del área bruta del diafragma.} \\ \textit{También  existe  irregularidad  cuando,  en  cualquiera de  los pisos y para cualquiera de las direcciones de análisis, se tiene alguna sección transversal del diafragma con un área neta resistente menor que 25\% del área de la sección transversal total de la misma dirección calculada con las dimensiones totales de la planta.}'))
        obj.append(mbox)
        
        fig = Figure(position='ht!')
        fig.append(NoEscape(r'\centering'))
        fig.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma}'))
        fig.append(NoEscape(r'\includegraphics[scale=0.7]{i_diafragma.PNG}'))
        fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
        obj.append(fig)
        
        if sec_change:
            data = [['Longitud del aligerado (L1)',sec_change['aligerado'][0],'m'],
                    ['Espesor del aligerado (e1)',sec_change['aligerado'][1],'m'],
                    ['Area del aligerado A1=L1$\\cdot$ e1','area1','$m^2$'],
                    ['Longitud de la losa macisa (L2)',sec_change['macisa'][0],'m'],
                    ['Espesor de la losa macisa (e2)',sec_change['macisa'][1],'m'],
                    ['Area de la losa macisa A1=L1$\\cdot$ e1','area2','$m^2$'],
                    ['Ratio','ratio','\%'],
                    ['Ratio límite','25.00','\%'],
                    ['Verificación','','']]
            
            data[2][1] = '%.2f'%(sec_change['aligerado'][0]*sec_change['aligerado'][1])
            data[5][1] = '%.2f'%(sec_change['macisa'][0]*sec_change['macisa'][1])
            data[6][1] = '%.2f'%(float(data[5][1])/float(data[2][1])*100)
            data[8][1] = r'\textcolor[rgb]{ .267,  .447,  .769}{\textbf{Regular}}' if float(data[6][1]) > float(data[7][1]) else r'\textcolor[rgb]{ 1,  0,  0}{\textbf{Irregular}}'
            
            table = Table(position='H')
            table.append(NoEscape(r'\centering'))
            table.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma (a)}'))
            tab = Tabular('|ll|c|r')
            tab.append(NoEscape(r'\cline{1-3}'))
            for row in data:
                tab.append(NoEscape(r'\multicolumn{2}{|l|}{%s} & %s & \multicolumn{1}{l}{%s} \\'%(row[0],row[1],row[2])))
                tab.append(NoEscape(r'\cline{1-3}'))
            table.append(tab)
            obj.append(table)
    
        if openings:
            data = [[r'\textbf{Abertura}', r'\textbf{Largo (m)}',r'\textbf{Ancho (m)}',r'\textbf{Área $m^2$}'],]
            
            for i,j in enumerate(openings['aberturas']):
                data.append([i+1,'%.2f'%(j[0]),'%.2f'%(j[1]),'%.2f'%(j[0]*j[1])])
            
            a_total = sum(float(i[3]) for i in data[1:])
            a_planta = openings['area_planta']
            ratio = a_total/a_planta*100
            verif = r'\textcolor[rgb]{ .267,  .447,  .769} {Regular}' if ratio < 50 else r'\textcolor[rgb]{ 1,  0,  0}{Irregular}'

            table = Table(position='H')
            table.append(NoEscape(r'\centering'))
            table.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma (b)}'))
            tab = Tabular('cccc')
            tab.add_hline()
            for row in data:
                tab.add_row([NoEscape(cell) for cell in row])
                tab.add_hline()
            tab.add_row(('',MultiColumn(2,data='Área total de aberturas:',align='r'),NoEscape(r'%.2f $m^2$'%a_total)))
            tab.add_row(('',MultiColumn(2,data='Área total de la planta:',align='r'),NoEscape(r'%.2f $m^2$'%a_planta)))
            tab.add_row(('',MultiColumn(2,data='Ratio:',align='r'),NoEscape(r'{:.2f} \%'.format(ratio))))
            tab.add_row(('',MultiColumn(2,data='Ratio límite:',align='r'),NoEscape('50.00 \%')))
            tab.add_row(('',MultiColumn(2,data='Verificación:',align='r'),NoEscape(verif)))
            table.append(tab)
            obj.append(table)

         


    
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.getcwd()+'\\..')
    from lib import etabs_utils as etb
    from lib import sismo_utils as sis
    import comtypes.client
    # from lib import sismo_utils as sis

    _, _SapModel = etb.connect_to_etabs()
    #Definir variables de salida 'Ton_m_C' o 'kgf_cm_C'
    etb.set_units(_SapModel,'Ton_m_C')


    sistemas = ['Pórticos de Concreto Armado',
                'Dual de Concreto Armado',
                'De Muros Estructurales de Concreto Armado',
                'Pórticos Especiales de Acero Resistentes a Momentos',
                'Pórticos Intermedios de Acero Resistentes a Momentos',
                'Pórticos Ordinarios de Acero Resistentes a Momentos',
                'Pórticos Especiales de Acero Concénticamente Arriostrados',
                'Pórticos Ordinarios de Acero Concénticamente Arriostrados',
                'Pórticos Acero Excéntricamente Arriostrados',
                'Muros de Ductilidad Limita de Concreto Armado',
                'Albañilería Armada o Confinada',
                'Madera']

    datos = {'Factor de Importancia': 'C',
            'Sistema Estructural': sistemas[0],
            'Número de Pisos': '4',
            'Número de Sotanos': '0',
            'Número de Azoteas': '0',
            'Factor Zona': '2',
            'Factor Suelo': 'S2',
            'Piso Blando': 'False',
            'Piso Blando Extremo': 'False',
            'Irregularidad de Masa': 'False',
            'Irregularidad Vertical': 'False',
            'Dicontinuidad Vertical': 'False',
            'Dicontinuidad Vertical Extrema': 'False',
            'Irregularidad Torsional': 'False',
            'Irregulariad Torsional Extrema': 'False',
            'Esquinas Entrantes': 'False',
            'Discontinuidad del diafragma': 'False',
            'Sistemas no Paralelos': 'False'}
    
    sismo = sis.sismo_e30(data=datos)
    # sismo.show_params()
    sismo.analisis_sismo(_SapModel)
    
    zona = 2
    suelo = 'S1'
    categoria = 'A2'

    geometry_options = { "left": "2.5cm", "top": "1.5cm" }
    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package('xcolor', options=['dvipsnames']))
    
    
    s1 = Section('Análisis Sísmico')

    coments = 'Las rigideces laterales pueden calcularse como la razon entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relativo en el centro de masas, ambos evaluados para la misma condición de carga. \n'

    factor_zona(s1, zona, insert=coments, o_type=Subsection)
    s1.append(coments)
    factor_suelo(s1, zona, suelo, insert=coments, o_type=Subsection)
    periodos_suelo(s1, suelo)   
    s1.append(coments)
    sist_estructural(s1, insert=coments, o_type=Subsection)
    factor_amplificacion(s1, insert=coments, o_type=Subsection)
    factor_importancia(s1,categoria)
    table = sismo.modal
    ana_modal(s1, table, insert=coments, o_type=Subsubsection)
    tabla = sismo.piso_blando_table
    sis_x = tabla[tabla['OutputCase']=='SDx Max']
    sis_y = tabla[tabla['OutputCase']=='SDy Max']
    irreg_rigidez(s1,sis_x,sis_y, insert=coments, o_type=Subsubsection)
    masa = sismo.rev_masa_table
    irreg_masa(s1,masa, insert=coments, o_type=Subsection)
    tabla = sismo.torsion_table
    sis_x = tabla[tabla['OutputCase']=='SDx Max']
    sis_y = tabla[tabla['OutputCase']=='SDy Max']
    s1.append(NoEscape(r'\newpage'))
    irreg_torsion(s1, sis_x, sis_y)
    sec_change = {'aligerado':[7.51,0.05],
                  'macisa':[2.25,0.20]}
    openings = {'aberturas':[(4.02,2.3),(1.1,2.3),(1.2,19)],
                'area_planta' : 120.41}
    irreg_esquinas(s1, sec_change=sec_change, openings=openings)

    
    doc.append(s1)
    doc.append(coments)
    doc.generate_pdf('Memoria Sismo2')
    doc.generate_tex('Memoria Sismo2')
            